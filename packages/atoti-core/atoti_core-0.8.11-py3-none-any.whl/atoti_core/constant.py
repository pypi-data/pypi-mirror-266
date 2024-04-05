from __future__ import annotations

import math
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, time

# Here `get_args()` is used on `Union`, not on `Literal`.
from typing import (  # pylint: disable=preferred-function
    NoReturn,
    Union,
    get_args,
)
from warnings import warn
from zoneinfo import ZoneInfo

from typing_extensions import TypeGuard

from .data_type import DataType, is_primitive_type
from .deprecated_warning_category import DEPRECATED_WARNING_CATEGORY

_ConstantArrayElement = Union[float, int]

ConstantValue = Union[
    bool,
    date,
    datetime,
    float,
    int,
    Sequence[_ConstantArrayElement],
    str,
    time,
]

_CONSTANT_ARRAY_ELEMENT_TYPES = get_args(_ConstantArrayElement)


def _get_checked_value_and_data_type(  # noqa: C901, PLR0911, PLR0912
    value: ConstantValue, /
) -> tuple[ConstantValue, DataType]:
    # Use the widest types to avoid compilation problems.
    # For better performance, types are checked from the most probable to the least.

    if isinstance(value, bool):
        return value, "boolean"
    if isinstance(value, float):
        if math.isnan(value):
            raise ValueError(
                f"`{value}` is not a valid constant value. To compare against NaN, use `isnan()` instead."
            )

        return value, "double"
    if isinstance(value, int):
        return value, "long"
    if isinstance(value, str):
        return value, "String"
    if isinstance(value, datetime):
        return value, "LocalDateTime" if value.tzinfo is None else "ZonedDateTime"
    if isinstance(value, date):
        return value, "LocalDate"
    if isinstance(value, time):
        return value, "LocalTime"
    if isinstance(value, tuple):
        # `tuple` is intentionally not supported so that branches of `Union[ConstantValue, tuple[ConstantValue, ...]]` can be distinguised with an `isinstance(value, tuple)` check.
        # This is used for `switch()`'s `cases` parameter for instance.
        # This can be removed in 0.9.0 as `switch()` will stop accepting tuples.
        raise TypeError(
            "Tuples are not valid constant values. Use lists for constant arrays instead."
        )
    if isinstance(value, list):
        if len(value) == 0:
            raise ValueError(
                "Empty arrays are not supported as their data type cannot be inferred."
            )

        invalid_array_element_type = next(
            (
                type(element)
                for element in value
                if not isinstance(element, _CONSTANT_ARRAY_ELEMENT_TYPES)
            ),
            None,
        )

        if invalid_array_element_type:
            raise TypeError(
                f"Expected all the elements of the constant array to have a type of `{[valid_type.__name__ for valid_type in _CONSTANT_ARRAY_ELEMENT_TYPES]}` but got `{invalid_array_element_type.__name__}`."
            )

        # Lists are stored as tuples to ensure full immutability.
        if any(isinstance(element, float) for element in value):
            if not all(isinstance(element, float) for element in value):
                warn(
                    "Heterogeneous arrays mixing ints and floats are deprecated, all elements must have the same type.",
                    category=DEPRECATED_WARNING_CATEGORY,
                    stacklevel=2,
                )

            return tuple(float(element) for element in value), "double[]"

        return tuple(int(element) for element in value), "long[]"

    raise TypeError(f"Unexpected constant value type: `{type(value).__name__}`.")


def is_constant_value(value: object, /) -> TypeGuard[ConstantValue]:
    try:
        Constant(value)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
    except (TypeError, ValueError):
        return False
    else:
        return True


# Arrays not supported yet.
ConstantJson = Union[bool, float, int, str]


# See Atoti Server's `LocalDateTimeParser.DEFAULT_PATTERN` and similar constants.
_JAVA_DATE_PATTERN = r"%Y-%m-%d"
_JAVA_TIME_PATTERN_WITHOUT_SECONDS = "%H:%M"
_JAVA_FULL_TIME_PATTERN = f"{_JAVA_TIME_PATTERN_WITHOUT_SECONDS}:%S"
_UTC_OFFSET_SUPPORTED_PATTERN = r"^(?P<sign>[+-])(?P<hours>\d{2})(?P<minutes>\d{2})$"


def _get_java_time_pattern(value: Union[datetime, time], /) -> str:
    return (
        _JAVA_FULL_TIME_PATTERN if value.second else _JAVA_TIME_PATTERN_WITHOUT_SECONDS
    )


@dataclass(frozen=True)
class Constant:  # pylint: disable=keyword-only-dataclass
    data_type: DataType = field(init=False, compare=False, repr=False)
    value: ConstantValue

    def __post_init__(self) -> None:
        value, data_type = _get_checked_value_and_data_type(self.value)
        self.__dict__["data_type"] = data_type
        self.__dict__["value"] = value

    def __lt__(self, other: object, /) -> bool:  # noqa: C901
        if not isinstance(other, Constant):
            raise TypeError(
                f"Cannot compare `{Constant.__name__}` to `{type(other).__name__}`."
            )

        def raise_type_error() -> NoReturn:
            raise TypeError(
                f"Cannot compare `{self.data_type}` `{Constant.__name__}` to `{other.data_type}` `{Constant.__name__}`."
            )

        if isinstance(self.value, (bool, int, float)):
            if not isinstance(other.value, (bool, int, float)):
                raise_type_error()
            return self.value < other.value

        if isinstance(self.value, str):
            if not isinstance(other.value, str):
                raise_type_error()
            return self.value < other.value

        if isinstance(self.value, Sequence):
            if not isinstance(other.value, Sequence):
                raise_type_error()
            return tuple(self.value) < tuple(other.value)

        if isinstance(self.value, date):
            if not isinstance(other.value, date):
                raise_type_error()
            return self.value < other.value

        if isinstance(self.value, datetime):
            if not isinstance(other.value, date):
                raise_type_error()
            return self.value < other.value

        # All the other types have already been handled.
        assert isinstance(self.value, time)

        if not isinstance(other.value, time):
            raise_type_error()
        return self.value < other.value

    @property
    def json(self) -> ConstantJson:
        if is_primitive_type(self.data_type) or self.data_type == "String":
            assert isinstance(self.value, (bool, float, int, str))
            return self.value

        if self.data_type == "LocalTime":
            assert isinstance(self.value, time)
            return self.value.strftime(_get_java_time_pattern(self.value))

        if self.data_type == "LocalDate":
            assert isinstance(self.value, (date, datetime))
            return self.value.strftime(_JAVA_DATE_PATTERN)

        if self.data_type == "LocalDateTime":
            assert isinstance(self.value, (date, datetime))
            time_pattern = (
                _get_java_time_pattern(self.value)
                if isinstance(self.value, datetime)
                else _JAVA_TIME_PATTERN_WITHOUT_SECONDS
            )
            return self.value.strftime(f"{_JAVA_DATE_PATTERN}T{time_pattern}")

        if self.data_type == "ZonedDateTime":
            assert isinstance(self.value, datetime)
            assert self.value.tzinfo

            timezone_name = self.value.tzname()
            assert timezone_name

            suffix: str
            time_pattern = _JAVA_FULL_TIME_PATTERN

            if timezone_name.lower() == "utc":
                time_pattern = _get_java_time_pattern(self.value)
                suffix = "Z[UTC]"
            else:
                offset = self.value.strftime("%z")
                match = re.match(_UTC_OFFSET_SUPPORTED_PATTERN, offset)
                assert match
                offset = f"{match.group('sign')}{match.group('hours')}:{match.group('minutes')}"

                if isinstance(self.value.tzinfo, ZoneInfo):
                    suffix = f"[{self.value.tzinfo.key}]"
                else:
                    timezone_name = self.value.tzname()
                    assert timezone_name
                    suffix = f"[{timezone_name}{offset}]"

                suffix = f"{offset}{suffix}"

            return (
                f"{self.value.strftime(f'{_JAVA_DATE_PATTERN}T{time_pattern}{suffix}')}"
            )

        raise NotImplementedError(
            f"Cannot convert constant `{self.value}` of type `{self.data_type}` to JSON."
        )
