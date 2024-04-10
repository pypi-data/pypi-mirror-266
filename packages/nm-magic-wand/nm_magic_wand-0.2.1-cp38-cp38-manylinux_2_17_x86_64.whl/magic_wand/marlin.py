import numpy
import torch

from magic_wand.quant_utils import (
    get_pack_factor,
    quantize_weights,
    sort_weights,
    SUPPORTED_GROUP_SIZES,
)

MARLIN_SUPPORTED_NUM_BITS = [4]
MARLIN_SUPPORTED_GROUP_SIZES = SUPPORTED_GROUP_SIZES

MARLIN_ACT_ORDER = [False, True]
MARLIN_K_FULL = [False, True]

MARLIN_TILE = 16
MARLIN_MIN_THREAD_N = 64
MARLIN_MIN_THREAD_K = 128
MARLIN_MAX_PARALLEL = 16


# Precompute permutations for Marlin weight and scale shuffling
#
# Marlin works on [16,64] tiles. The goal of the permutations is to reorder the weight data so that it is compatible
# with the tensor-core format that is described here:
# https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#matrix-fragments-for-mma-m16n8k16-with-floating-point-type
#
# As a result of this reordering, the vector loads inside the kernel will get the data as it is needed for tensor-core
# (without the need to use ldmatrix instructions)
def _get_perms():
    perm = []
    for i in range(32):
        perm1 = []
        col = i // 4
        for block in [0, 1]:
            for row in [
                    2 * (i % 4),
                    2 * (i % 4) + 1,
                    2 * (i % 4 + 4),
                    2 * (i % 4 + 4) + 1,
            ]:
                perm1.append(16 * row + col + 8 * block)
        for j in range(4):
            perm.extend([p + 256 * j for p in perm1])

    perm = numpy.array(perm)
    interleave = numpy.array([0, 2, 4, 6, 1, 3, 5, 7])
    perm = perm.reshape((-1, 8))[:, interleave].ravel()
    perm = torch.from_numpy(perm)
    scale_perm = []
    for i in range(8):
        scale_perm.extend([i + 8 * j for j in range(8)])
    scale_perm_single = []
    for i in range(4):
        scale_perm_single.extend(
            [2 * i + j for j in [0, 1, 8, 9, 16, 17, 24, 25]])
    return perm, scale_perm, scale_perm_single


_perm, _scale_perm, _scale_perm_single = _get_perms()

__cuda_arch = torch.cuda.get_device_capability()


def is_marlin_supported():
    return __cuda_arch[0] >= 8


def is_marlin_compatible(weight_bits, group_size, is_sym):
    return (weight_bits in MARLIN_SUPPORTED_NUM_BITS
            and group_size in MARLIN_SUPPORTED_GROUP_SIZES and is_sym)


def marlin_repack_from_gptq(
    gptq_b_q_weight: torch.Tensor,
    perm: torch.Tensor,
    size_k: int,
    size_n: int,
):
    if not is_marlin_supported():
        raise RuntimeError(
            f"marlin_repack_from_gptq requires CUDA ARCH >= 8.0. The current arch is {__cuda_arch}"
        )

    return torch.ops.nm_ops.marlin_repack_from_gptq(
        gptq_b_q_weight,
        perm,
        size_k,
        size_n,
    )


def marlin_permute_weights(q_w, size_k, size_n, num_bits, tile=MARLIN_TILE):
    assert q_w.shape == (size_k, size_n)
    assert size_k % tile == 0, f"size_k = {size_k}, tile = {tile}"
    assert size_n % tile == 0, f"size_k = {size_n}, tile = {tile}"

    # Permute weights to 16x64 marlin tiles
    q_w = q_w.reshape((size_k // tile, tile, size_n // tile, tile))
    q_w = q_w.permute((0, 2, 1, 3))
    q_w = q_w.reshape((size_k // tile, size_n * tile))

    q_w = q_w.reshape((-1, _perm.numel()))[:, _perm].reshape(q_w.shape)

    return q_w


def marlin_weights(q_w, size_k, size_n, num_bits):
    # Permute
    q_w = marlin_permute_weights(q_w, size_k, size_n, num_bits)

    # Pack
    pack_factor = get_pack_factor(num_bits)
    orig_device = q_w.device

    q_w = q_w.cpu().numpy().astype(numpy.uint32)
    q_packed = numpy.zeros((q_w.shape[0], q_w.shape[1] // pack_factor),
                           dtype=numpy.uint32)

    for i in range(pack_factor):
        q_packed |= q_w[:, i::pack_factor] << num_bits * i

    q_packed = torch.from_numpy(q_packed.astype(numpy.int32)).to(orig_device)

    return q_packed


def marlin_permute_scales(s, size_k, size_n, group_size):
    if group_size < size_k and group_size != -1:
        s = s.reshape((-1, len(_scale_perm)))[:, _scale_perm]
    else:
        s = s.reshape((-1, len(_scale_perm_single)))[:, _scale_perm_single]
    s = s.reshape((-1, size_n)).contiguous()

    return s


def marlin_quantize(
    w: torch.Tensor,
    num_bits: int,
    group_size: int,
    act_order: bool,
):
    size_k, size_n = w.shape

    # Normalize group_size
    if group_size == -1:
        group_size = size_k
    assert group_size <= size_k

    # Quantize (and apply act_order if provided)
    w_ref, q_w, s, g_idx, rand_perm = quantize_weights(w, num_bits, group_size,
                                                       act_order)

    # For act_order, sort the "weights" and "g_idx" so that group ids are increasing
    sort_indices = torch.empty(0, dtype=torch.int, device=w.device)
    if act_order:
        q_w, g_idx, sort_indices = sort_weights(q_w, g_idx)

    # Reformat to marlin
    marlin_q_w = marlin_weights(q_w, size_k, size_n, num_bits)
    marlin_s = marlin_permute_scales(s, size_k, size_n, group_size)

    # Create result
    res_list = [w_ref, marlin_q_w, marlin_s, g_idx, sort_indices, rand_perm]
    for i in range(len(res_list)):
        res_list[i] = res_list[i].to(w.device)

    return res_list


class MarlinWorkspace:

    def __init__(self, out_features):
        assert (
            out_features % MARLIN_MIN_THREAD_N == 0
        ), "out_features = {out_features} is not divisible by MARLIN_MIN_THREAD_N = {MARLIN_MIN_THREAD_N}"

        max_workspace_size = (out_features //
                              MARLIN_MIN_THREAD_N) * MARLIN_MAX_PARALLEL

        self.scratch = torch.zeros(max_workspace_size,
                                   dtype=torch.int,
                                   device="cuda")


def marlin_gemm(
    a: torch.Tensor,
    b_q_weight: torch.Tensor,
    b_scales: torch.Tensor,
    g_idx: torch.Tensor,
    perm: torch.Tensor,
    workspace: torch.Tensor,
    size_m: int,
    size_n: int,
    size_k: int,
    is_k_full: bool,
):
    if not is_marlin_supported():
        raise RuntimeError(
            f"marlin_gemm requires CUDA ARCH >= 8.0. The current arch is {__cuda_arch}"
        )

    return torch.ops.nm_ops.marlin_gemm(
        a,
        b_q_weight,
        b_scales,
        g_idx,
        perm,
        workspace,
        size_m,
        size_n,
        size_k,
        is_k_full,
    )
