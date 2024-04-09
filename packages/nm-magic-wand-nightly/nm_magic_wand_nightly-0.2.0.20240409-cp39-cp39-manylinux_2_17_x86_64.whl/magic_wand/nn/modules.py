import math

import torch
from torch import nn

import magic_wand.functional as F
from magic_wand import SparseTensor
from magic_wand.utils import sparsify_


class SparseParameter(torch.nn.Parameter):
    def __new__(cls, data):
        self = SparseTensor.from_dense(data)
        self._is_param = True
        return self


class SparseLinear(nn.Linear):
    def __init__(
        self,
        in_features,
        out_features,
        rnd_sparsity=0.5,
        has_bias=True,
        device=None,
        dtype=None,
        weight_data=None,
        bias_data=None,
    ):
        if isinstance(device, str):
            device = torch.device(device)

        # `requires_grad=False` since `SparseTensor` does not support `requires_grad` yet
        # `requires_grad=True` is not needed for LORA so this should be fine for our cases
        factory_kwargs = {"device": device, "dtype": dtype, "requires_grad": False}

        super(nn.Linear, self).__init__()

        self.in_features = in_features
        self.out_features = out_features

        # Init random weights (if not provided)
        if weight_data is None:
            weight_data = torch.rand((out_features, in_features), **factory_kwargs)
            if device is not torch.device("meta"):
                sparsify_(weight_data, rnd_sparsity)

        self.weight = SparseParameter(weight_data)
        if has_bias:
            # Do not use meta device for bias
            if factory_kwargs["device"] == torch.device("meta"):
                factory_kwargs["device"] = torch.device("cpu")

            # Init random bias (if not provided)
            if bias_data is None:
                bias_data = nn.Parameter(torch.empty(out_features, **factory_kwargs))

                # No reset_parameters so manually init here
                fan_in, _ = nn.init._calculate_fan_in_and_fan_out(self.weight)
                bound = 1 / math.sqrt(fan_in) if fan_in > 0 else 0
                nn.init.uniform_(bias_data, -bound, bound)

            self.bias = bias_data
        else:
            self.register_parameter("bias", None)

    def reset_parameters(self) -> None:
        raise NotImplementedError

    def forward(self, x: torch.Tensor):
        return F.sparse_linear(x, self.weight, self.bias)
