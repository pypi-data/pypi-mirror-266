from __future__ import annotations

from typing import Literal, Optional, Union

from .constant import Constant
from .hierarchy_identifier import HierarchyIdentifier
from .level_identifier import LevelIdentifier
from .operation import Condition, ConditionComparisonOperatorBound

QueryFilter = Condition[
    Union[HierarchyIdentifier, LevelIdentifier],
    ConditionComparisonOperatorBound,
    Constant,
    Optional[Literal["and"]],
]
