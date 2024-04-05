from collections.abc import Collection
from dataclasses import dataclass
from typing import Literal, NoReturn, Optional, Union

from typing_extensions import override

from .combine_conditions import combine_conditions
from .constant import Constant
from .hierarchy_identifier import HierarchyIdentifier
from .identifier import Identifier
from .level_identifier import LevelIdentifier
from .operation import ComparisonCondition, Condition, ConditionCombinationOperatorBound


@dataclass(frozen=True)
class HierarchyIsinCondition(
    Condition[HierarchyIdentifier, Literal["isin"], Constant, None]
):
    subject: HierarchyIdentifier
    level_names: tuple[str, ...]
    _member_paths: frozenset[tuple[Constant, ...]]

    def __init__(
        self,
        *,
        subject: HierarchyIdentifier,
        level_names: tuple[str, ...],
        member_paths: Collection[tuple[Constant, ...]],
    ) -> None:
        if not member_paths:
            raise ValueError(
                "No passed member paths, the condition will always evaluate to `False`."
            )

        for member_path in member_paths:
            if not member_path:
                raise ValueError(
                    "Passed one empty member path: it is unnecessary since it will always evaluate to `False`."
                )

            if len(member_path) > len(level_names):
                raise ValueError(
                    f"Member path `{tuple(member.value for member in member_path)}` contains more than {len(level_names)} elements which is the number of levels of `{subject!r}`."
                )

        self.__dict__["subject"] = subject
        self.__dict__["level_names"] = level_names
        self.__dict__["_member_paths"] = frozenset(member_paths)

    @property
    def member_paths(self) -> tuple[tuple[Constant, ...], ...]:
        # The member paths are sorted to ensure predictability.
        return tuple(sorted(self._member_paths))

    @property
    def normalized(
        self,
    ) -> Condition[
        Union[HierarchyIdentifier, LevelIdentifier],
        Literal["eq", "isin"],
        Constant,
        Optional[Literal["and"]],
    ]:
        if len(self.member_paths) != 1:
            return self

        return combine_conditions(
            (
                [
                    ComparisonCondition(
                        subject=LevelIdentifier(self.subject, level_name),
                        operator="eq",
                        target=member,
                    )
                    for level_name, member in zip(
                        self.level_names, next(iter(self.member_paths))
                    )
                ],
            )
        )

    @property
    def combined_comparison_condition(
        self,
    ) -> Condition[
        LevelIdentifier, Literal["eq"], Constant, ConditionCombinationOperatorBound
    ]:
        return combine_conditions(
            [
                [
                    ComparisonCondition(
                        subject=LevelIdentifier(self.subject, level_name),
                        operator="eq",
                        target=member,
                    )
                    for level_name, member in zip(self.level_names, member_path)
                ]
                for member_path in self.member_paths
            ]
        )

    @property
    @override
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        return frozenset([type(self.subject)])

    @override
    def __invert__(
        self,
    ) -> NoReturn:
        raise RuntimeError(f"A `{type(self).__name__}` cannot be inverted.")
        # It can actually be done using `~hierarchy_isin_condition.combined_comparison_condition` but this changes the type of `subject` which breaks the contract of `Condition.__invert__()`.

    @override
    def __repr__(self) -> str:
        return f"{self.subject!r}.isin{tuple(tuple(member.value for member in member_path) for member_path in self.member_paths)!r}"
