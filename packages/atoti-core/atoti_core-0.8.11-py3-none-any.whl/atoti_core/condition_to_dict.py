from typing import Literal, Optional

from .condition_to_pairs import condition_to_pairs
from .has_identifier import IdentifierT_co
from .operation import Condition, ConditionTargetT_co


def condition_to_dict(
    condition: Condition[
        IdentifierT_co,
        Literal["eq"],
        ConditionTargetT_co,
        Optional[Literal["and"]],
    ],
    /,
) -> dict[IdentifierT_co, ConditionTargetT_co]:
    pairs = condition_to_pairs(condition)
    result: dict[IdentifierT_co, ConditionTargetT_co] = {}

    for identifier, target in pairs:
        if identifier in result:
            raise ValueError(
                f"Expected the combined condition to have distinct subjects but got `{identifier!r}` twice."
            )

        result[identifier] = target

    return result
