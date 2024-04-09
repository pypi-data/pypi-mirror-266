import torch


# Inherit from Function
class SparseLinearFunction(torch.autograd.Function):
    """
    Same as LinearFunction (see https://pytorch.org/docs/stable/notes/extending.html)
        but decompresses the sparse tensor before each operation
    """

    @staticmethod
    def forward(input, weight, bias):
        dense_weight = weight.to_dense().to(input.dtype).t()
        input_is_vector = input.dim() == 1

        if input_is_vector:
            input = input.unsqueeze(0)

        output = torch.matmul(input, dense_weight)

        # Free memory, not sure if this is needed, here to just be safe
        del dense_weight

        if bias is not None:
            output += bias.unsqueeze(0).expand_as(output)

        if input_is_vector:
            output = output.squeeze(0)

        return output

    @staticmethod
    def setup_context(ctx, inputs, output):
        input, weight, bias = inputs
        ctx.save_for_backward(input, weight, bias)

    @staticmethod
    def backward(ctx, grad_output):
        input, weight, bias = ctx.saved_tensors
        grad_input = grad_weight = grad_bias = None

        grad_output_is_vector = grad_output.dim() == 1
        if grad_output_is_vector:
            grad_output = grad_output.unsqueeze(0)

        if ctx.needs_input_grad[0]:
            dense_weight = weight.to_dense().to(input.dtype)
            grad_input = torch.matmul(grad_output, dense_weight)
            # Free memory, not sure if this is needed, here to just be safe
            del dense_weight
        if ctx.needs_input_grad[1]:
            assert "getting the gradient of the weights is not supportted for now since it should return a sparse tensor matching the sparsity of the weights"
        if bias is not None and ctx.needs_input_grad[2]:
            grad_bias = grad_output.sum(0)

        if grad_output_is_vector:
            grad_input = grad_input.squeeze(0)

        return grad_input, grad_weight, grad_bias


def sparse_linear(input, weight, bias):
    return SparseLinearFunction.apply(input, weight, bias)
