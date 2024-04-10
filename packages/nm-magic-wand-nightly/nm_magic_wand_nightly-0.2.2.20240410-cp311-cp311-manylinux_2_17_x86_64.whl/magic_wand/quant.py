import numpy
import torch

from magic_wand.quant_utils import get_pack_factor, quantize_weights


def quant_quantize(w: torch.Tensor, num_bits: int, group_size: int):
    pack_factor = get_pack_factor(num_bits)

    # Quantize
    w_ref, q_w, s, g_idx, rand_perm = quantize_weights(w, num_bits, group_size, False)

    # Pack (over columns)
    assert (
        q_w.shape[1] % pack_factor == 0
    ), f"q_w.shape = {q_w.shape} has shape[1] = {q_w.shape[1]} and it must be divisible by pack_factor = {pack_factor}"

    q_w = q_w.cpu().numpy().astype(numpy.uint32)
    q_packed = numpy.zeros(
        (q_w.shape[0], q_w.shape[1] // pack_factor), dtype=numpy.uint32
    )

    for i in range(pack_factor):
        q_packed |= q_w[:, i::pack_factor] << (i * num_bits)

    q_packed = torch.from_numpy(q_packed.astype(numpy.int32)).to(w.device)

    # Finish
    w_ref = w_ref.to(w.device)
    s = s.to(w.device)

    return w_ref, q_packed, s


def dequant_b_q_weight(
    b_q_weight: torch.Tensor,
    b_scales: torch.Tensor,
    num_bits: int,
    group_size: int,
    a_ref: torch.Tensor,
    size_m: int,
    size_n: int,
    size_k: int,
):
    return torch.ops.nm_ops.dequant_b_q_weight(
        b_q_weight, b_scales, num_bits, group_size, a_ref, size_m, size_n, size_k
    )


def quant_gemm(
    a: torch.Tensor,
    b_q_weight: torch.Tensor,
    b_scales: torch.Tensor,
    num_bits: int,
    group_size: int,
    size_m: int,
    size_n: int,
    size_k: int,
):
    return torch.ops.nm_ops.quant_gemm(
        a, b_q_weight, b_scales, num_bits, group_size, size_m, size_n, size_k
    )


def cublas_gemm(a: torch.Tensor, b_weight: torch.Tensor):
    return torch.ops.nm_ops.cublas_gemm(a, b_weight)
