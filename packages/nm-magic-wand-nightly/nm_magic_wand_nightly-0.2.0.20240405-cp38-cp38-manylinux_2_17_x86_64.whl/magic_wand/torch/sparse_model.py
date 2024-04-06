import numpy
import torch

import magic_wand
import magic_wand.nn


class SparseConfig:
    def __init__(self, min_sparsity=0.3):
        self.min_sparsity = min_sparsity


def tensor_sparsity(data):
    nz_count = float(torch.count_nonzero(data))
    total_count = numpy.prod(data.shape)

    density = nz_count / total_count
    sparsity = 1.0 - density

    return sparsity


def _replace_with_sparse_linear(
    model,
    replace_funcs,
    modules_to_not_convert=[],
    current_key_name=None,
    sparse_config=None,
    log=False,
):
    for name, module in model.named_children():
        # Update recursion key
        if current_key_name is None:
            current_key_name = []
        current_key_name.append(name)

        full_name = ".".join(current_key_name)

        # Determine if replace allowed
        replace_allowed = (name not in modules_to_not_convert) and (
            not any(key in full_name for key in modules_to_not_convert)
        )

        # Apply replace functions
        if replace_allowed:
            for replace_func in replace_funcs:
                if replace_func(model, full_name, name, module):
                    if log:
                        print(f"Replaced: {full_name}")
                    break

        if len(list(module.children())) > 0:
            _ = _replace_with_sparse_linear(
                module,
                replace_funcs,
                modules_to_not_convert,
                current_key_name,
                sparse_config,
                log=log,
            )
        # Remove the last key for recursion
        current_key_name.pop(-1)

    return model


def replace_with_sparse_linear(
    model,
    modules_to_not_convert=[],
    has_loaded_weights=True,
    current_key_name=None,
    sparse_config=None,
    log=False,
):
    """
    Enables sparse compression by replacing all `torch.nn.Linear` modules with `magic_wand.nn.SparseLinear` modules.

    Parameters:
        model (`torch.nn.Module`):
            Input model
        modules_to_not_convert:
            Module names to skip conversion
        has_loaded_weights:
            Whether to use (and compress) the already loaded weights
        current_key_name (`List[`str`]`, *optional*):
            An array to track the current key of the recursion
        sparse_config:
            TODO Add docs and features as necessary
    """

    def replace_nn_linear(model, full_name, name, module):
        if not isinstance(module, torch.nn.Linear):
            return False

        device = "meta"
        weight_data = None
        bias_data = None

        if has_loaded_weights:
            device = "cpu"
            weight_data = module.weight
            bias_data = module.bias

            # Apply sparse config
            if sparse_config:
                cur_sparsity = tensor_sparsity(weight_data)
                if cur_sparsity < sparse_config.min_sparsity:
                    if log:
                        print(
                            "Skip due to low sparsity ({} < expected_min {}) for: {}".format(
                                cur_sparsity, sparse_config.min_sparsity, full_name
                            )
                        )
                    return False

        model._modules[name] = magic_wand.nn.SparseLinear(
            module.in_features,
            module.out_features,
            rnd_sparsity=0.5,
            has_bias=bias_data is not None,
            device=device,
            dtype=None,
            weight_data=weight_data,
            bias_data=bias_data,
        )

        return True

    model = _replace_with_sparse_linear(
        model,
        [replace_nn_linear],
        modules_to_not_convert=modules_to_not_convert,
        current_key_name=current_key_name,
        sparse_config=sparse_config,
        log=log,
    )

    return model
