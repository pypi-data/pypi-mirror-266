import torch
from torch.sparse import to_sparse_semi_structured, SparseSemiStructuredTensor

USE_GPU = True

"""
NM in-house sparsity utils
"""


def sparsify(tensor, sparsity, inplace=False, use_gpu=USE_GPU):
    ret = tensor
    with torch.no_grad():
        # Remove current zeros
        cur_zero_mask = tensor == 0
        if inplace:
            tensor.masked_fill_(cur_zero_mask, 1)
        else:
            ret = tensor.masked_fill(cur_zero_mask, 1)

        # Apply sparsity
        if use_gpu:
            rand_tensor = torch.rand(*tensor.shape, device="cuda").to(
                device=tensor.device
            )
        else:
            rand_tensor = torch.rand(*tensor.shape)

        new_zero_mask = rand_tensor < sparsity
        if inplace:
            tensor.masked_fill_(new_zero_mask, 0)
        else:
            ret = tensor.masked_fill(new_zero_mask, 0)

    return ret


def sparsify_(tensor, sparsity):
    return sparsify(tensor, sparsity, inplace=True)


"""
Wrap PyTorch semi-structured 2:4 sparsity utils.

Default to CUTLASS
"""

SparseSemiStructuredTensor._FORCE_CUTLASS = True  # Default CUTLASS
TORCH_SEMI_STRUCTURED_LIB_CUTLASS = 0
TORCH_SEMI_STRUCTURED_LIB_CUSPARSELT = 1
NV_SEMI_STRUCTURED_LIB_CUTLASS = 2
NV_SEMI_STRUCTURED_LIB_CUSPARSELT = 3


def is_torch_semi_structured_lib(tensor_lib):
    # True if torch.sparse semi-structured 2:4 library is in use
    return (tensor_lib == TORCH_SEMI_STRUCTURED_LIB_CUTLASS) or (
        tensor_lib == TORCH_SEMI_STRUCTURED_LIB_CUSPARSELT
    )


def is_cutlass(tensor_lib):
    # True is CUTLASS kernel is being used directly or indirectly
    return (tensor_lib == TORCH_SEMI_STRUCTURED_LIB_CUTLASS) or (
        tensor_lib == NV_SEMI_STRUCTURED_LIB_CUTLASS
    )


def random_mat_semi_structured_pruned_fp16(M, K):
    mask = torch.Tensor([0, 0, 1, 1]).tile((M, K // 4)).cuda().bool()
    mat = torch.rand(M, K).half().cuda()
    mat = mat.masked_fill_(mat == 0, 1)
    return mat * mask


def compress_to_torch_sparse_semi_structured_mat(mat: torch.Tensor):
    if isinstance(mat, SparseSemiStructuredTensor):
        # Already compressed
        return mat

    return to_sparse_semi_structured(mat.cuda())


def decompress_torch_sparse_semi_structured_mat(sp_mat):
    if not isinstance(sp_mat, SparseSemiStructuredTensor):
        if isinstance(sp_mat, torch.Tensor):
            return sp_mat
        else:
            assert False, (
                "sp_mat type "
                + type(sp_mat).__name__
                + " is invalid for decompression."
            )
    return sp_mat.to_dense()


def random_mat_semi_structured_pruned_compressed_fp16(M, K):
    return compress_to_torch_sparse_semi_structured_mat(
        random_mat_semi_structured_pruned_fp16(M, K)
    )


def get_torch_semi_structured_lib():
    if SparseSemiStructuredTensor._FORCE_CUTLASS:
        return TORCH_SEMI_STRUCTURED_LIB_CUTLASS
    else:
        return TORCH_SEMI_STRUCTURED_LIB_CUSPARSELT


def set_torch_semi_structured_lib(lib_id):
    if lib_id == TORCH_SEMI_STRUCTURED_LIB_CUTLASS:
        SparseSemiStructuredTensor._FORCE_CUTLASS = True
    elif lib_id == TORCH_SEMI_STRUCTURED_LIB_CUSPARSELT:
        SparseSemiStructuredTensor._FORCE_CUTLASS = False
    else:
        print("Warning: torch semi structured lib unchanged.")


"""
Test support routines
"""

"""Default relative tolerance for checking FP16 arithmetic results"""
default_fp16_matmul_rtol = 1e-3
default_bfp16_matmul_rtol = 1e-2
default_matmul_rtol_map = {
    torch.float16: default_fp16_matmul_rtol,
    torch.bfloat16: default_bfp16_matmul_rtol,
}


def print_actual_atol_rtol(a, b):
    """
    Assuming an allclose has failed, compute atol and rtol
    values which on their own would have caused the allclose to pass.
    """
    abs_diff = torch.abs(a - b)
    max_abs_diff = torch.max(abs_diff)

    # Avoid division by zero for relative difference
    with torch.no_grad():
        rel_diff = torch.where(
            a != 0, abs_diff / torch.abs(a), torch.tensor(float("inf"))
        )
    max_rel_diff = torch.max(rel_diff)

    # Suggesting atol and rtol values
    suggested_atol = max_abs_diff * 1.1  # 10% higher than max absolute difference
    suggested_rtol = max_rel_diff * 1.1  # 10% higher than max relative difference

    print(f"Suggested atol: {suggested_atol.item()}")
    print(f"Suggested rtol: {suggested_rtol.item()}")


def allclose_else_print_assert(a, b, rtol=None):
    """
    Wraps torch.allclose. Upon torch.allclose failure,
    prints suggested rtol value, then fails an assert.

    If no rtol arg is provided, default to torch.allclose default
    rtol. atol is always torch.allclose default.
    """
    is_allclose = False
    if rtol is not None:
        is_allclose = torch.allclose(a, b, rtol=rtol)
    else:
        is_allclose = torch.allclose(a, b)

    if not is_allclose:
        print_actual_atol_rtol(a, b)

    assert is_allclose
