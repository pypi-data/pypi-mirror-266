from collections.abc import Mapping
from typing import Literal

PANDAS_NULLABLE_DTYPE_TO_NON_NULLABLE_DTYPE: Mapping[
    str,
    Literal["bool", "float32", "float64", "int32", "int64"],
] = {
    "boolean": "bool",
    "Float32": "float32",
    "Float64": "float64",
    "Int32": "int32",
    "Int64": "int64",
}
