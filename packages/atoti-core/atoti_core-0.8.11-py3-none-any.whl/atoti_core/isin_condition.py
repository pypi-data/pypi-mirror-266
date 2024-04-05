from collections.abc import Collection
from dataclasses import dataclass
from typing import Literal, Optional, TypeVar

from typing_extensions import override

from .combine_conditions import combine_conditions
from .constant import Constant
from .hierarchy_identifier import HierarchyIdentifier
from .identifier import Identifier
from .operation import (
    ComparisonCondition,
    Condition,
    ConditionCombinationOperatorBound,
    ConditionComparisonOperatorBound,
    ConditionSubjectT_co,
)

IsinConditionElementT_co = TypeVar(
    "IsinConditionElementT_co", bound=Optional[Constant], covariant=True
)


@dataclass(frozen=True)
class IsinCondition(
    Condition[ConditionSubjectT_co, Literal["isin"], IsinConditionElementT_co, None]
):
    subject: ConditionSubjectT_co
    _elements: frozenset[IsinConditionElementT_co]

    def __init__(
        self,
        *,
        subject: ConditionSubjectT_co,
        elements: Collection[IsinConditionElementT_co],
    ) -> None:
        assert not isinstance(
            subject, HierarchyIdentifier
        ), "Conditions on hierarchies must use `HierarchyIsinCondition`."

        if not elements:
            raise ValueError(
                "No passed elements, the condition will always evaluate to `False`."
            )

        self.__dict__["subject"] = subject
        self.__dict__["_elements"] = frozenset(elements)

    @property
    def elements(self) -> tuple[IsinConditionElementT_co, ...]:
        # The elements are sorted to ensure predictability.
        return (  # pyright: ignore[reportReturnType]
            # Collections containing `None` cannot be sorted.
            # If `None` is in the elements it's added at the head of the tuple.
            # The remaining non-`None` elements are sorted and inserted after.
            *([None] if None in self._elements else []),  # type: ignore[arg-type]
            *sorted(element for element in self._elements if element is not None),  # type: ignore[type-var]
        )

    @property
    def normalized(
        self,
    ) -> Condition[
        ConditionSubjectT_co, Literal["eq", "isin"], IsinConditionElementT_co, None
    ]:
        if len(self.elements) != 1:
            return self

        return ComparisonCondition(
            subject=self.subject, operator="eq", target=self.elements[0]
        )

    @property
    def combined_comparison_condition(
        self,
    ) -> Condition[
        ConditionSubjectT_co,
        Literal["eq"],
        IsinConditionElementT_co,
        Optional[Literal["or"]],
    ]:
        return combine_conditions(
            [
                (
                    ComparisonCondition(
                        subject=self.subject, operator="eq", target=element
                    ),
                )
                for element in self.elements
            ]
        )

    @property
    @override
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        return self._get_identifier_types(self.subject)

    @override
    def __invert__(
        self,
    ) -> Condition[
        ConditionSubjectT_co,
        ConditionComparisonOperatorBound,
        IsinConditionElementT_co,
        ConditionCombinationOperatorBound,
    ]:
        return ~self.combined_comparison_condition

    @override
    def __repr__(self) -> str:
        return f"{self.subject!r}.isin{tuple(element.value if isinstance(element, Constant) else element for element in self.elements)!r}"


IsinConditionBound = IsinCondition[Identifier, Optional[Constant]]
