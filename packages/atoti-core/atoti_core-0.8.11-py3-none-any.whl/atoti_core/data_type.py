from typing import Any, Literal, cast

from typing_extensions import TypeGuard

from .get_literal_args import get_literal_args

BooleanDataType = Literal["boolean"]
DoubleArrayDataType = Literal["double[]"]
DoubleDataType = Literal["double"]
FloatArrayDataType = Literal["float[]"]
FloatDataType = Literal["float"]
IntArrayDataType = Literal["int[]"]
IntDataType = Literal["int"]
LocalDateDataType = Literal["LocalDate"]
LocalDateTimeDataType = Literal["LocalDateTime"]
LocalTimeDataType = Literal["LocalTime"]
LongArrayDataType = Literal["long[]"]
LongDataType = Literal["long"]
ObjectArrayDataType = Literal["Object[]"]
ObjectDataType = Literal["Object"]
StringDataType = Literal["String"]
ZonedDateTimeDataType = Literal["ZonedDateTime"]


# Order matters: a type can be widened to the previous type.
NumericDataType = Literal[DoubleDataType, FloatDataType, LongDataType, IntDataType]

PrimitiveDataType = Literal[BooleanDataType, NumericDataType]

# Order matters: a type can be widened to the previous type.
DateDataType = Literal[
    ZonedDateTimeDataType,
    LocalDateTimeDataType,
    LocalDateDataType,
]

TimeDataType = Literal[LocalTimeDataType]

TemporalDataType = Literal[DateDataType, TimeDataType]

# Must be ordered as `NumericDataType`.
NumericArrayDataType = Literal[
    DoubleArrayDataType,
    FloatArrayDataType,
    LongArrayDataType,
    IntArrayDataType,
]

ArrayDataType = Literal[NumericArrayDataType, ObjectArrayDataType]

# Built from the hierarchy of data types.
# Should contain all the data types.
_AggregatedDataType = Literal[
    PrimitiveDataType,
    ArrayDataType,
    TemporalDataType,
    ObjectDataType,
    StringDataType,
]

# Flat list of data types to make them easier to read in the API Reference/IDEs/Type checkers.
DataType = Literal[
    "boolean",
    "double",
    "double[]",
    "float",
    "float[]",
    "int",
    "int[]",
    "LocalDate",
    "LocalDateTime",
    "LocalTime",
    "long",
    "long[]",
    "Object",
    "Object[]",
    "String",
    "ZonedDateTime",
]

_ARRAY_SUFFIX = "[]"


def parse_data_type(value: str, /) -> DataType:
    value = value.lower()

    try:
        return next(
            cast(Any, data_type)
            for data_type in get_literal_args(DataType)
            if value == cast(str, data_type).lower()
        )
    except StopIteration as error:
        raise TypeError(f"""Expected a data type but got "{value}".""") from error


def is_array_type(data_type: DataType, /) -> TypeGuard[ArrayDataType]:
    return data_type in get_literal_args(ArrayDataType)


def to_array_type(data_type: DataType, /) -> ArrayDataType:
    data_type = parse_data_type(f"{data_type}{_ARRAY_SUFFIX}")
    if not is_array_type(data_type):
        raise TypeError(f"Expected {data_type} to be an array type.")
    return data_type


def is_date_type(data_type: DataType, /) -> TypeGuard[DateDataType]:
    return data_type in get_literal_args(DateDataType)


def is_time_type(data_type: DataType, /) -> TypeGuard[TimeDataType]:
    return data_type in get_literal_args(TimeDataType)


def is_temporal_type(data_type: DataType, /) -> TypeGuard[TemporalDataType]:
    return data_type in get_literal_args(TemporalDataType)


def is_numeric_type(data_type: DataType, /) -> TypeGuard[NumericDataType]:
    return data_type in get_literal_args(NumericDataType)


def is_numeric_array_type(data_type: DataType, /) -> TypeGuard[NumericArrayDataType]:
    return data_type in get_literal_args(NumericArrayDataType)


def get_numeric_array_element_type(
    data_type: NumericArrayDataType, /
) -> NumericDataType:
    return cast(NumericDataType, parse_data_type(data_type[: -len(_ARRAY_SUFFIX)]))


def is_boolean_type(data_type: DataType, /) -> TypeGuard[BooleanDataType]:
    return data_type in get_literal_args(BooleanDataType)


def is_primitive_type(data_type: DataType, /) -> TypeGuard[PrimitiveDataType]:
    return data_type in get_literal_args(PrimitiveDataType)
