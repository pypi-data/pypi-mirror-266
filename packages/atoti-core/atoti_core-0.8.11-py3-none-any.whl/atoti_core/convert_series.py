from __future__ import annotations

from collections.abc import Collection, Mapping
from functools import cache
from typing import Any, Literal

import numpy as np
import pandas as pd

from .data_type import (
    DataType,
    NumericDataType,
    get_numeric_array_element_type,
    is_array_type,
    is_date_type,
    is_numeric_array_type,
    is_numeric_type,
    is_time_type,
)
from .get_package_version import get_package_version
from .pandas_nullable_dtype_to_non_nullable_dtype import (
    PANDAS_NULLABLE_DTYPE_TO_NON_NULLABLE_DTYPE,
)

_ARRAY_SEPARATOR = ";"

_NUMERIC_DATA_TYPE_TO_NULLABLE_DTYPE: Mapping[
    NumericDataType,
    Literal["Float32", "Float64", "Int32", "Int64"],
] = {
    "double": "Float64",
    "float": "Float32",
    "int": "Int32",
    "long": "Int64",
}

_TIMEZONE_FIRST_CHARACTER = "["


@cache
def _is_using_pandas_1() -> bool:
    return get_package_version("pandas").startswith("1.")


def convert_series(  # noqa: PLR0911
    series: pd.Series[Any],
    /,
    *,
    data_type: DataType,
    nullable: bool,
) -> Collection[object]:
    if is_numeric_type(data_type):
        nullable_dtype = _NUMERIC_DATA_TYPE_TO_NULLABLE_DTYPE[data_type]
        return series.astype(
            nullable_dtype
            if nullable
            else PANDAS_NULLABLE_DTYPE_TO_NON_NULLABLE_DTYPE[nullable_dtype]
        )

    if data_type == "boolean":
        return series.astype("boolean" if nullable else "bool")

    if data_type == "String":
        return series.astype("string")

    if is_array_type(data_type):
        array_dtype = (
            PANDAS_NULLABLE_DTYPE_TO_NON_NULLABLE_DTYPE[
                _NUMERIC_DATA_TYPE_TO_NULLABLE_DTYPE[
                    get_numeric_array_element_type(data_type)
                ]
            ]
            if is_numeric_array_type(data_type)
            else "object"
        )
        return pd.Series(
            [
                None
                if array is None
                else np.array(
                    array.split(_ARRAY_SEPARATOR) if isinstance(array, str) else array,
                    dtype=array_dtype,
                )
                for array in series
            ],
            dtype="object",
            index=series.index,
        )

    if is_date_type(data_type):
        if data_type == "ZonedDateTime":
            series = pd.Series(
                [
                    # Keep offset but remove time zone name that pandas cannot parse.
                    zoned_date_time.split(_TIMEZONE_FIRST_CHARACTER, maxsplit=1)[0]
                    if isinstance(zoned_date_time, str)
                    else zoned_date_time
                    for zoned_date_time in series
                ],
                dtype="object",
                index=series.index,
            )

        # `datetime.date` instances become `pandas.Timestamp` instances because they are more compact/performant.
        # When all timestamps in a series/column share 00:00:00 for their time, pandas will display them as dates anyway.
        return (
            pd.to_datetime(series, infer_datetime_format=True)
            if _is_using_pandas_1()
            else pd.to_datetime(series, format="ISO8601")
        )

    if is_time_type(data_type):
        return pd.to_timedelta(series)

    return series
