from enum import Enum


class TensorSpec:
    # TODO[VIMPORTANT] CHECK AND MAKE FUNCTIONS PRIVATE IF THEY SHOULD NOT BE ACCESSIBLE DIRECTLY

    _type = "tensor_spec"

    def __init__(self, *, dtype=None, shape=None, name=None) -> None:

        self.dtype = dtype
        self.shape = shape
        self.name = name

    def __repr__(self) -> str:
        return f"TensorSpec(name={str(self.name)}, shape={str(self.shape)}, data_type={str(self.dtype)})"

    def to_dict(self):
        return {
            "type": self._type,
            "dtype": self.dtype.value,
            "shape": self.shape,
            "name": self.name,
        }


class DataType(Enum):
    # TODO[VIMPORTANT] CHECK AND MAKE FUNCTIONS PRIVATE IF THEY SHOULD NOT BE ACCESSIBLE DIRECTLY

    INT8 = "int8"
    INT16 = "int16"
    INT32 = "int32"
    INT64 = "int64"
    UINT8 = "uint8"
    UINT16 = "uint16"
    UINT32 = "uint32"
    UINT64 = "uint64"
    QINT8 = "qint8"
    QINT16 = "qint16"
    QINT32 = "qint32"
    QUINT8 = "quint8"
    QUINT16 = "quint16"
    FLOAT16 = "float16"
    FLOAT32 = "float32"
    FLOAT64 = "float64"
    COMPLEX64 = "complex64"
    COMPLEX128 = "complex128"
    STRING = "string"
    BOOL = "bool"
    VARIANT = "variant"
