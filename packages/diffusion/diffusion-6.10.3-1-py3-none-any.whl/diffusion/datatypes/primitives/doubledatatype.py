from .primitivedatatype import PrimitiveDataType


class DoubleDataType(PrimitiveDataType[float]):
    """Data type that supports double-precision floating point numbers.

    (Eight-byte IEEE 754)

    The integer value is serialized as CBOR-format binary. A serialized value
    can be read as a JSON instance.
    """

    type_code = 19
    type_name = "double"
