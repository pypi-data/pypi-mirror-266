from collections.abc import Mapping
from typing import Literal, cast

from .get_literal_args import get_literal_args

ComparisonOperator = Literal["eq", "ge", "gt", "le", "lt", "ne"]

ALL_COMPARISON_OPERATORS = cast(
    tuple[ComparisonOperator, ...], get_literal_args(ComparisonOperator)
)

_OPERATOR_TO_INVERSE_OPERATOR_ONE_WAY: Mapping[
    ComparisonOperator, ComparisonOperator
] = {
    "eq": "ne",
    "lt": "ge",
    "le": "gt",
}

OPERATOR_TO_INVERSE_OPERATOR: Mapping[ComparisonOperator, ComparisonOperator] = cast(
    Mapping[ComparisonOperator, ComparisonOperator],
    {
        **_OPERATOR_TO_INVERSE_OPERATOR_ONE_WAY,
        **{value: key for key, value in _OPERATOR_TO_INVERSE_OPERATOR_ONE_WAY.items()},
    },
)
