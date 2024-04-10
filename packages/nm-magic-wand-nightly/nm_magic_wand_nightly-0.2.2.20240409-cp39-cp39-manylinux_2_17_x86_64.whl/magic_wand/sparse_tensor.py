import torch
from typing import Type
from magic_wand.semi_structured import (
    semi_structured_sparse_dense_gemm,
    semi_structured_dense_sparse_T_gemm,
)
from magic_wand.compressed_storage_format import (
    CompressedStorageFormat,
    SparseBitmaskStorageFormat,
    SparseSemiStructuredStorageFormat,
)


class SparseTensor(torch.Tensor):
    @staticmethod
    def __new__(
        cls,
        shape: torch.Size,
        dtype: torch.dtype,
        storage_format_cls: Type[CompressedStorageFormat],
        compressed_data: CompressedStorageFormat = None,
    ):
        assert torch.__version__ > (1, 10), "SparseTensor requires PyTorch 1.11+"
        self = torch.Tensor._make_wrapper_subclass(cls, size=shape, dtype=dtype)

        self.storage_format_cls = storage_format_cls
        self.compressed_data = compressed_data

        return self

    def has_compressed_data(self):
        return self.compressed_data is not None

    def narrow(self, dim, start, length, layout=torch.strided):
        raise Exception("narrow(..) is not implemented for SparseTensor")

    def __repr__(self):
        return f"SparseTensor(shape={self.shape}, dtype={self.dtype}, storage_format_cls={self.storage_format_cls}, has_compressed_data={self.has_compressed_data()})"

    @classmethod
    def from_dense(
        cls, data: torch.Tensor, storage_format_cls=SparseBitmaskStorageFormat
    ):
        if data.is_meta:
            compressed_data = None
        else:
            compressed_data = storage_format_cls.compress(data)

        return cls(data.shape, data.dtype, storage_format_cls, compressed_data)

    @classmethod
    def _copy(cls, arg0, arg1):
        assert arg0.shape == arg1.shape

        if arg0.has_compressed_data():
            arg0.compressed_data.copy_(arg1)
        else:
            arg0.compressed_data = arg0.storage_format_cls.compress(arg1)

        return arg0

    @classmethod
    def _to_dense(cls, self):
        if self.has_compressed_data():
            return self.compressed_data.decompress()
        else:
            return torch.empty(size=self.shape, dtype=self.dtype, device="meta")

    @classmethod
    def _to(cls, arg0, device, *args):
        if isinstance(device, str):
            device = torch.device(device)
        assert isinstance(device, torch.device)

        if device == torch.device("meta"):
            return cls(arg0.shape, arg0.dtype, arg0.storage_format_cls, None)
        else:
            return cls(
                arg0.shape,
                arg0.dtype,
                arg0.storage_format_cls,
                arg0.compressed_data.to(device, *args),
            )

    @classmethod
    def _maybe_dense_dispatch(cls, func, types, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}

        # TODO: check if there is a better way to check this than hackily looking for a trailing "_"
        inplace = kwargs.get("inplace", False) or func.__name__[-1] == "_"

        if func.__name__ == "__get__":
            with torch._C.DisableTorchFunction():
                return func(*args, **kwargs)

        if func.__name__ == "__set__":
            with torch._C.DisableTorchFunction():
                return func(*args, **kwargs)

        if func in [torch.Tensor.copy_]:
            assert len(args) == 2
            return cls._copy(args[0], args[1])

        if func == torch.Tensor.cuda:
            return cls._to(args[0], torch.device("cuda"))

        # TODO: add torch.Tensor.cpu, but decide if it should copy compressed or dense

        if func == torch.Tensor.to:
            # only support to device for now, not to type
            assert len(args) >= 2
            return cls._to(*args)

        if func == torch.Tensor.to_dense:
            assert len(args) == 1
            return cls._to_dense(args[0])

        if func == torch.Tensor.requires_grad_:
            assert len(args) == 2
            assert args[0].has_compressed_data()

            args[0].compressed_data.requires_grad_(args[1])
            return args[0]

        if func == torch.Tensor.is_floating_point:
            return args[0].is_floating_point

        if func == torch.Tensor.detach or func.__name__ == "detach.default":
            if args[0].has_compressed_data():
                return cls(
                    args[0].shape,
                    args[0].dtype,
                    args[0].storage_format_cls,
                    args[0].compressed_data.detach(),
                )
            else:
                return cls(
                    args[0].shape, args[0].dtype, args[0].storage_format_cls, None
                )

        if func.__name__ == "_has_compatible_shallow_copy_type":
            # TODO: hack for now maybe we should be able  support shallow copies pretty easily
            #  just haven't reaserched it enough, used for parameter sharing
            return False

        ret = None
        dense_args = []

        # TODO: revisit dispatch logic after MVP
        if (
            (func.__name__ == "matmul" or func.__name__ == "linear")
            and len(args) == 2
            and len(kwargs) == 0
        ):
            if (
                (not isinstance(args[0], cls))
                and isinstance(args[1], cls)
                and args[1].storage_format_cls == SparseSemiStructuredStorageFormat
                and args[1].transpose
            ):
                # 2nd arg SparseSemiStructuredStorageFormat
                compressed_data = args[1].compressed_data
                return semi_structured_dense_sparse_T_gemm(args[0], compressed_data)
            elif (
                isinstance(args[0], cls)
                and args[0].storage_format_cls == SparseSemiStructuredStorageFormat
                and (not isinstance(args[1], cls))
            ):
                # 1st arg SparseSemiStructuredStorageFormat
                compressed_data = args[0].compressed_data
                return semi_structured_sparse_dense_gemm(compressed_data, args[1])
            else:
                # Not SparseSemiStructuredStorageFormat
                # For now we just decompress to dense and run the op as dense
                # Preserve dense_args to help free decompressed matrices
                dense_args = [
                    arg if not isinstance(arg, cls) else cls._to_dense(arg)
                    for arg in args
                ]

                ret = func(*dense_args, **kwargs)

        else:
            # Not SparseSemiStructuredStorageFormat
            # For now we just decompress to dense and run the op as dense
            # Preserve dense_args to help free decompressed matrices
            dense_args = [
                arg if not isinstance(arg, cls) else cls._to_dense(arg) for arg in args
            ]

            ret = func(*dense_args, **kwargs)

        # Update the first arg in-place if its an inplace op, this assumes that the first arg
        # is "self". Im not sure if this is the case with args in `__torch_function__` and
        # `__torch_dispatch__` but seems reasonable and works
        if isinstance(args[0], cls) and inplace:
            storage_format_cls = args[0].compressed_data.__class__
            ret = cls.from_dense(ret, storage_format_cls=storage_format_cls)
            args[0].copy_(ret)

        # Clean up memory and modify in place if required
        for idx, arg in enumerate(args):
            if isinstance(arg, cls):
                del dense_args[idx]

        return ret

    @classmethod
    def __torch_function__(cls, func, types, args=(), kwargs=None):
        return cls._maybe_dense_dispatch(func, types, args, kwargs)

    @classmethod
    def __torch_dispatch__(cls, func, types, args, kwargs):
        return cls._maybe_dense_dispatch(func, types, args, kwargs)
