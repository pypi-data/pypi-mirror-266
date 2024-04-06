from .quant_utils import (
    SUPPORTED_GROUP_SIZES,
    SUPPORTED_NUM_BITS,
    get_pack_factor,
    quantize_weights,
    sort_weights,
    gptq_pack,
)

from .quant import (
    cublas_gemm,
    dequant_b_q_weight,
    quant_gemm,
    quant_quantize,
)

from .marlin import (
    marlin_weights,
    marlin_quantize,
    marlin_permute_scales,
    marlin_repack_from_gptq,
    MarlinWorkspace,
    is_marlin_supported,
    is_marlin_compatible,
    marlin_gemm,
    MARLIN_SUPPORTED_NUM_BITS,
    MARLIN_SUPPORTED_GROUP_SIZES,
    MARLIN_ACT_ORDER,
    MARLIN_K_FULL,
    MARLIN_TILE,
    MARLIN_MIN_THREAD_N,
    MARLIN_MIN_THREAD_K,
    MARLIN_MAX_PARALLEL,
)

from .semi_structured import (
    semi_structured_sparse_dense_gemm,
    semi_structured_dense_sparse_T_gemm,
)

from .compressed_storage_format import (
    CompressedStorageFormat,
    SparseBitmaskStorageFormat,
    SparseBEGemmStorageFormat,
    SparseSemiStructuredStorageFormat,
)

from .sparse_tensor import SparseTensor

from .utils import (
    sparsify_,
    TORCH_SEMI_STRUCTURED_LIB_CUTLASS,
    TORCH_SEMI_STRUCTURED_LIB_CUSPARSELT,
)

__all__ = [
    "SparseTensor",
    "CompressedStorageFormat",
    "SparseBitmaskStorageFormat",
    "SparseBEGemmStorageFormat",
    "SparseSemiStructuredStorageFormat",
    "sparsify",
    "sparsify_",
    "get_pack_factor",
    "quantize_weights",
    "sort_weights",
    "gptq_pack",
    "quant_quantize",
    "dequant_b_q_weight",
    "SUPPORTED_NUM_BITS",
    "SUPPORTED_GROUP_SIZES",
    "quant_gemm",
    "cublas_gemm",
    "TORCH_SEMI_STRUCTURED_LIB_CUTLASS",
    "TORCH_SEMI_STRUCTURED_LIB_CUSPARSELT",
    "semi_structured_sparse_dense_gemm",
    "semi_structured_dense_sparse_T_gemm",
    "marlin_weights",
    "marlin_quantize",
    "marlin_permute_scales",
    "marlin_repack_from_gptq",
    "MarlinWorkspace",
    "is_marlin_supported",
    "is_marlin_compatible",
    "marlin_gemm",
    "MARLIN_SUPPORTED_NUM_BITS",
    "MARLIN_SUPPORTED_GROUP_SIZES",
    "MARLIN_ACT_ORDER",
    "MARLIN_K_FULL",
    "MARLIN_TILE",
    "MARLIN_MIN_THREAD_N",
    "MARLIN_MIN_THREAD_K",
    "MARLIN_MAX_PARALLEL",
]


def import_ops():
    import torch
    from pathlib import Path

    script_dir = Path(__file__).parent.resolve()
    torch.ops.load_library(f"{script_dir}/nm_ops.so")


import_ops()
