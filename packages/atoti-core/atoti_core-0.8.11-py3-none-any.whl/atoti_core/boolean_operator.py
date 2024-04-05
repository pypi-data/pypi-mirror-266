from typing import Literal, cast

from .get_literal_args import get_literal_args

BooleanOperator = Literal["and", "or"]

ALL_BOOLEAN_OPERATORS = cast(
    tuple[BooleanOperator, ...], get_literal_args(BooleanOperator)
)
