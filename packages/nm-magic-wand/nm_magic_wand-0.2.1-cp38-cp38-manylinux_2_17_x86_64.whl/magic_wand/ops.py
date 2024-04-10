import torch

from magic_wand.compressed_storage_format import SparseBEGemmStorageFormat


def be_ds_gemm(A: torch.Tensor, B: SparseBEGemmStorageFormat) -> torch.Tensor:
    assert A.dtype == B.compute_type
    return torch.ops.nm_ops.be_ds_gemm(
        A,
        B.layout_id,
        B.values,
        B.offsets,
        B.counts,
        B.bitmasks,
        B.max_nnz_in_tile,
        B.out_feature_dim_extent,
        SparseBEGemmStorageFormat.shared_locks[B.device],
        B.compute_type,
    )
