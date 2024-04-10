import torch

from magic_wand.compressed_storage_format import SparseBEGemmStorageFormat


# TODO: coordinate rename to bemma_mm with nm-vllm
def be_ds_gemm(
    A: torch.Tensor,
    B: SparseBEGemmStorageFormat,
    scale: float = None,
    zero_point: int = None,
) -> torch.Tensor:
    assert A.dtype == B.compute_type
    return torch.ops.nm_ops.bemma_ds_mm(
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
        scale,
        zero_point,
    )
