import builtins
import copy
import os
import torch
import dataclasses
import warnings
from typing import ClassVar, Dict
from torch.sparse import SparseSemiStructuredTensor
from typing import Optional

from magic_wand.utils import (
    sparsify_,
    TORCH_SEMI_STRUCTURED_LIB_CUTLASS,
    is_torch_semi_structured_lib,
    is_cutlass,
    set_torch_semi_structured_lib,
    compress_to_torch_sparse_semi_structured_mat,
    decompress_torch_sparse_semi_structured_mat,
)


class CompressedStorageFormat:
    # if used as decorator on the a subclass, will provide default
    #  implementations of `copy_`, `device`, `etc.`
    _dataclass = dataclasses.dataclass()

    @classmethod
    def compress(cls, uncompressed: torch.Tensor):
        raise NotImplementedError

    def decompress(self):
        raise NotImplementedError

    @property
    def _fieldnames(self):
        return [x.name for x in dataclasses.fields(self)]

    @property
    def _ref_field(self):
        return getattr(self, self._fieldnames[0])

    @property
    def device(self) -> torch.device:
        return self._ref_field.device

    @property
    def requires_grad(self) -> builtins.bool:
        return self._ref_field.requires_grad

    @property
    def layout(self) -> torch.layout:
        return self._ref_field.layout

    def apply_to_tensors_(self, func):
        for fieldname in self._fieldnames:
            if isinstance(getattr(self, fieldname), torch.Tensor):
                func(getattr(self, fieldname))

    def copy_(self, arg):
        if isinstance(arg, self.__class__):
            for fieldname in self._fieldnames:
                arg_field_data = getattr(arg, fieldname)
                # TODO: post-MVP - more general implementation, i.e. SparseSemiStructuredTensor
                # in-place copy
                if isinstance(getattr(self, fieldname), torch.Tensor) and (
                    not isinstance(getattr(self, fieldname), SparseSemiStructuredTensor)
                ):
                    getattr(self, fieldname).resize_as_(arg_field_data).copy_(
                        arg_field_data
                    )
                else:
                    setattr(self, fieldname, arg_field_data)
            return self
        else:
            new = self.compress(arg.cpu()).to(arg.device)
            return self.copy_(new)

    def to(self, device, *args):
        if isinstance(device, str):
            device = torch.device(device)
        assert isinstance(device, torch.device)

        def to_device(attribute):
            if isinstance(attribute, torch.Tensor):
                # Do not apply the additional "args" at this point (else it may result in type conversion)
                # TODO: Expand logic based on need
                if len(args) > 0:
                    if args[0] is not None:  # args[0] is the new type
                        print(
                            "WARNING: CompressedStorageFormat to(..) function got a type conversion argument {args[0]} which is ignored"
                        )
                if isinstance(attribute, SparseSemiStructuredTensor):
                    return attribute
                else:
                    return attribute.to(device)

            return attribute

        cls = self.__class__
        return cls(
            **{
                fieldname: to_device(getattr(self, fieldname))
                for fieldname in self._fieldnames
            }
        )

    def cuda(self):
        return self.to(device="cuda")

    def detach(self):
        self.apply_to_tensors_(lambda x: x.detach())
        return self

    def requires_grad_(self, mode):
        self.apply_to_tensors_(lambda x: x.requires_grad_(mode))
        return self


@CompressedStorageFormat._dataclass
class UncompressedStorageFormat(CompressedStorageFormat):
    values: torch.Tensor

    @classmethod
    def compress(cls, uncompressed: torch.Tensor):
        return cls(
            values=torch.ops.nm_ops.mock_compress(uncompressed.cpu()).to(
                uncompressed.device
            )
        )

    def decompress(self):
        orig_device = copy.copy(self.values.device)
        return torch.ops.nm_ops.mock_decompress(self.values.cuda()).to(orig_device)


@CompressedStorageFormat._dataclass
class SparseBitmaskStorageFormat(CompressedStorageFormat):
    values: torch.Tensor
    value_offsets: torch.Tensor
    bitmasks: torch.Tensor
    inner_dim_extent: int

    @classmethod
    def compress(cls, uncompressed: torch.Tensor):
        impose_ks = os.getenv("SPARSE_TENSOR_IMPOSE_KS")
        if impose_ks:
            print(
                f"Imposing KS = {impose_ks} on uncompressed.shape = {uncompressed.shape}"
            )
            sparsify_(uncompressed, float(impose_ks))

        values, value_offsets, bitmasks = torch.ops.nm_ops.bitmask_compress(
            uncompressed.cpu()
        )
        return cls(
            values=values,
            value_offsets=value_offsets,
            bitmasks=bitmasks,
            inner_dim_extent=uncompressed.shape[-1],
        ).to(uncompressed.device)

    def decompress(self):
        orig_device = copy.copy(self.values.device)
        return torch.ops.nm_ops.bitmask_decompress(
            self.values.cuda(),
            self.value_offsets.cuda(),
            self.bitmasks.cuda(),
            self.inner_dim_extent,
        ).to(orig_device)


# TODO: coordinate rename to BemmaStorageFormat with nm-vllm
@CompressedStorageFormat._dataclass
class SparseBEGemmStorageFormat(CompressedStorageFormat):
    layout_id: str
    values: torch.Tensor
    offsets: torch.Tensor
    counts: torch.Tensor
    bitmasks: torch.Tensor
    max_nnz_in_tile: int
    out_feature_dim_extent: int
    reduction_extent: int  # K -> TODO better name (or deduce)
    locks_required: int
    compute_type: torch.dtype

    # use shared locks, currently this does not get deallocated
    shared_locks: ClassVar[Dict[torch.device, torch.Tensor]] = {}

    @classmethod
    def compress(cls, dense: torch.Tensor, compute_type: Optional[torch.dtype] = None):
        if compute_type is None:
            compute_type = dense.dtype
        if torch.cuda.get_device_capability() < (8, 0):
            raise NotImplementedError(
                "Optimized dense-sparse GEMM is not implemented for NVIDIA SM < 8.0"
            )

        impose_ks = os.getenv("SPARSE_TENSOR_IMPOSE_KS")
        if impose_ks:
            print(f"Imposing KS = {impose_ks} on dense.shape = {dense.shape}")
            sparsify_(dense, float(impose_ks))

        (
            layout_id,
            values,
            offsets,
            counts,
            bitmasks,
            max_nnz_in_tile,
            locks_required,
        ) = torch.ops.nm_ops.bemma_ds_compress(dense.cpu())
        return cls(
            layout_id=layout_id,
            values=values,
            offsets=offsets,
            counts=counts,
            bitmasks=bitmasks,
            max_nnz_in_tile=max_nnz_in_tile,
            out_feature_dim_extent=dense.shape[1],
            reduction_extent=dense.shape[0],
            locks_required=locks_required,
            compute_type=compute_type,
        ).to(dense.device)

    @property
    def _ref_field(self):
        return self.values

    def _create_locks(self, device):
        return torch.zeros(self.locks_required, dtype=torch.int32, device=device)

    def to(self, device, *args):
        ret = super(SparseBEGemmStorageFormat, self).to(device)
        device = ret.device

        # if we don't have a shared locks workspace on the device or
        #  the current one is too small allocate a new/larger one
        shared_locks = SparseBEGemmStorageFormat.shared_locks
        if (device not in shared_locks) or (
            shared_locks[device].numel() < self.locks_required
        ):
            shared_locks[device] = self._create_locks(device)

        return ret

    def decompress(self, scale: float = None, zero_point: int = None):
        return torch.ops.nm_ops.bemma_ds_decompress(
            self.layout_id,
            self.values,
            self.offsets,
            self.counts,
            self.bitmasks,
            self.max_nnz_in_tile,
            self.out_feature_dim_extent,
            self.reduction_extent,
            self.compute_type,
            scale,
            zero_point,
        )


@CompressedStorageFormat._dataclass
class SparseSemiStructuredStorageFormat(CompressedStorageFormat):
    # values: torch.Tensor
    # indices: torch.Tensor
    _encapsulated_torch_sparse_tensor: torch.Tensor
    _tensor_lib: int = TORCH_SEMI_STRUCTURED_LIB_CUTLASS

    @classmethod
    def compress(
        cls,
        uncompressed: torch.Tensor,
        tensor_lib: int = TORCH_SEMI_STRUCTURED_LIB_CUTLASS,
    ):
        # TODO: impose KS
        # impose_ks = os.getenv("SPARSE_TENSOR_IMPOSE_KS")
        # if impose_ks:
        #    print(f"Imposing KS = {impose_ks} on dense.shape = {dense.shape}")
        #    sparsify_(dense, float(impose_ks))
        with warnings.catch_warnings():
            # We supress warnings from PyTorch here about this pathway to the affect of:
            # "The PyTorch API of SparseSemiStructuredTensor is in prototype stage"
            warnings.filterwarnings("ignore", category=UserWarning)

            encapsulated_torch_sparse_tensor = (
                compress_to_torch_sparse_semi_structured_mat(uncompressed)
            )

        return cls(
            _encapsulated_torch_sparse_tensor=encapsulated_torch_sparse_tensor,
            _tensor_lib=tensor_lib,
        ).to(uncompressed.device)

    def decompress(self):
        orig_device = copy.copy(self.values().device)
        return decompress_torch_sparse_semi_structured_mat(
            self.encapsulated_torch_sparse_tensor
        ).to(orig_device)

    def uses_torch_semi_structured_lib(self):
        # True if torch.sparse semi-structured 2:4 library is in use
        return is_torch_semi_structured_lib(self.tensor_lib)

    def uses_cutlass(self):
        # True if CUTLASS is being utilized directly or indirectly
        return is_cutlass(self.tensor_lib)

    def force_tensor_lib(self):
        # Whichever torch.sparse semi-structured 2:4 wrapper this instance
        # uses (i.e. torch+CUTLASS, torch+cuSPARSELt), force it
        set_torch_semi_structured_lib(self.tensor_lib)

    @property
    def tensor_lib(self):
        return self._tensor_lib

    @tensor_lib.setter
    def tensor_lib(self, value):
        self._tensor_lib = value

    @property
    def encapsulated_torch_sparse_tensor(self):
        return self._encapsulated_torch_sparse_tensor

    @encapsulated_torch_sparse_tensor.setter
    def encapsulated_torch_sparse_tensor(self, value):
        # Read-only
        print(
            "Warning: encapsulated_torch_sparse_tensor is read-only yet SparseSemiStructuredStorageFormat.encapsulated_torch_sparse_tensor setter was called."
        )
        pass

    @property
    def values(self):
        return self.encapsulated_torch_sparse_tensor.values

    @values.setter
    def values(self, value):
        # Read-only
        print(
            "Warning: values is read-only yet SparseSemiStructuredStorageFormat.values setter was called."
        )
        pass

    @property
    def indices(self):
        return self.encapsulated_torch_sparse_tensor.indices

    @indices.setter
    def indices(self, value):
        # Read-only
        print(
            "Warning: indices is read-only yet SparseSemiStructuredStorageFormat.indices setter was called."
        )
        pass
