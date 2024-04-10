import torch

import torch.nn.functional as F

from magic_wand.compressed_storage_format import SparseSemiStructuredStorageFormat


def pad_tensor_to_multiple(tensor, row_factor):
    """
    Pad a 2D tensor with additional rows to make its number of rows a multiple of row_factor.

    Returns:
    - torch.Tensor: The padded tensor.
    - tuple: The range of valid (pre-padding) row indices as [a, b).
    """
    # Calculate the number of rows to add
    rows_needed = (row_factor - tensor.size(0) % row_factor) % row_factor
    if rows_needed > 0:
        # Pad the tensor. Padding format is (left, right, top, bottom), so we add rows at the bottom.
        padded_tensor = F.pad(tensor, (0, 0, 0, rows_needed))
    else:
        # No padding needed, return the original tensor
        padded_tensor = tensor

    # The valid range of row indices is from 0 to the original number of rows
    valid_range = (0, tensor.size(0))

    return padded_tensor, valid_range


def extract_valid_rows(C, valid_rows_range):
    """
    Extract valid rows from the result tensor C based on the valid_rows_range.

    Args:
    - C (torch.Tensor): The result tensor from a matrix multiplication A x B = C.
    - valid_rows_range (tuple): A tuple (a, b) representing the range of valid row indices in A.

    Returns:
    - torch.Tensor: Tensor containing only the valid rows from C.
    """
    # Unpack the valid_rows_range
    start, end = valid_rows_range

    # Check if the number of rows in C matches the size of the valid range
    if C.size(0) == end - start:
        # The number of rows in C matches the size of the valid range, return C as is
        return C
    else:
        # The number of rows in C is different, extract and return only the valid rows
        return C[start:end, :]


def semi_structured_sparse_dense_gemm(
    a: SparseSemiStructuredStorageFormat, b: torch.Tensor
):
    # 2:4 semi-structured sparse * dense has direct support by the PyTorch matmul wrapper
    assert (
        a.uses_torch_semi_structured_lib() and a.uses_cutlass()
    ), "Only CUTLASS via torch.sparse is supported for semi-structured 2:4 sparsity."

    a.force_tensor_lib()
    return a.encapsulated_torch_sparse_tensor @ b


def semi_structured_dense_sparse_T_gemm(
    a: torch.Tensor, b_T: SparseSemiStructuredStorageFormat
):
    # 2:4 semi-structured dense * sparse is computed via spare * dense kernel + TOPOT
    assert (
        b_T.uses_torch_semi_structured_lib() and b_T.uses_cutlass()
    ), "Only CUTLASS via torch.sparse is supported for semi-structured 2:4 sparsity."
    b_T.force_tensor_lib()

    a, valid_rows_range = pad_tensor_to_multiple(a, 8)
    return extract_valid_rows(
        F.linear(a, b_T.encapsulated_torch_sparse_tensor), valid_rows_range
    )
