from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from itertools import chain
from typing import (
    Generic,
    Literal,
    NoReturn,
    Optional,
    TypeVar,
    Union,
    overload,
)

from typing_extensions import override

from ._other_identifier import OtherIdentifierT_co
from .arithmetic_operator import ArithmeticOperator
from .boolean_operator import BooleanOperator
from .comparison_operator import OPERATOR_TO_INVERSE_OPERATOR, ComparisonOperator
from .constant import Constant, ConstantValue
from .data_type import DataType
from .has_identifier import HasIdentifier, IdentifierT_co
from .hierarchy_identifier import HierarchyIdentifier
from .identifier import Identifier
from .keyword_only_dataclass import keyword_only_dataclass


@overload
def convert_to_operand(value: None, /) -> None: ...


@overload
def convert_to_operand(value: ConstantValue, /) -> Constant: ...


@overload
def convert_to_operand(value: HasIdentifier[IdentifierT_co], /) -> IdentifierT_co: ...


@overload
def convert_to_operand(
    value: OperandCondition[IdentifierT_co],
    /,
) -> OperandCondition[IdentifierT_co]: ...


@overload
def convert_to_operand(
    value: Operation[IdentifierT_co], /
) -> Operation[IdentifierT_co]: ...


def convert_to_operand(
    value: Optional[
        Union[
            OperandCondition[IdentifierT_co],
            ConstantValue,
            HasIdentifier[IdentifierT_co],
            Operation[IdentifierT_co],
        ]
    ],
    /,
) -> Optional[Operand[IdentifierT_co]]:
    if value is None or isinstance(value, (Condition, Operation)):
        return value
    if isinstance(value, HasIdentifier):
        return value._identifier
    return Constant(value)


class OperandConvertible(Generic[IdentifierT_co], ABC):
    @property
    @abstractmethod
    def _operation_operand(self) -> NonConstantNonConditionOperand[IdentifierT_co]: ...

    def isnull(
        self,
    ) -> Condition[
        NonConstantNonConditionOperand[IdentifierT_co], Literal["eq"], None, None
    ]:
        """Return a condition evaluating to ``True`` when the element evaluates to ``None`` and ``False`` otherwise.

        Use `~obj.isnull()` for the opposite behavior.
        """
        return ComparisonCondition(
            subject=self._operation_operand,
            operator="eq",
            target=None,
        )

    def __bool__(self) -> NoReturn:
        raise AssertionError(
            f"Instances of `{type(self).__name__}` cannot be cast to a boolean. Use a comparison operator to create a `{Condition.__name__}` instead."
        )

    @override
    def __hash__(self) -> int:
        # The public API sometimes requires instances of this class to be used as mapping keys so they must be hashable.
        # However, these keys are only ever iterated upon (i.e. there is no get by key access) so the hash is not important.
        # The ID of the object is thus used, like `object.__hash__()` would do.
        return id(self)

    def __getitem__(
        self,
        index: Union[
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
            slice,
            tuple[int, ...],
            int,
        ],
        /,
    ) -> Operation[Union[IdentifierT_co, OtherIdentifierT_co]]:
        return IndexingOperation(
            operand=self._operation_operand,
            index=index._identifier
            if isinstance(index, HasIdentifier)
            else (
                index
                if isinstance(index, (slice, Operation))
                else Constant(list(index) if isinstance(index, tuple) else index)
            ),
        )

    @override
    # The signature is not compatible with `object.__eq__()` on purpose.
    def __eq__(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Condition[
        NonConstantNonConditionOperand[IdentifierT_co],
        Literal["eq"],
        Union[Constant, OtherIdentifierT_co, Operation[OtherIdentifierT_co]],
        None,
    ]:
        assert other is not None, "Use `isnull()` instead."
        return ComparisonCondition(
            subject=self._operation_operand,
            target=convert_to_operand(other),
            operator="eq",
        )

    def __ge__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Condition[
        NonConstantNonConditionOperand[IdentifierT_co],
        Literal["ge"],
        Union[Constant, OtherIdentifierT_co, Operation[OtherIdentifierT_co]],
        None,
    ]:
        return ComparisonCondition(
            subject=self._operation_operand,
            operator="ge",
            target=convert_to_operand(other),
        )

    def __gt__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Condition[
        NonConstantNonConditionOperand[IdentifierT_co],
        Literal["gt"],
        Union[Constant, OtherIdentifierT_co, Operation[OtherIdentifierT_co]],
        None,
    ]:
        return ComparisonCondition(
            subject=self._operation_operand,
            operator="gt",
            target=convert_to_operand(other),
        )

    def __le__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Condition[
        NonConstantNonConditionOperand[IdentifierT_co],
        Literal["le"],
        Union[Constant, OtherIdentifierT_co, Operation[OtherIdentifierT_co]],
        None,
    ]:
        return ComparisonCondition(
            subject=self._operation_operand,
            operator="le",
            target=convert_to_operand(other),
        )

    def __lt__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Condition[
        NonConstantNonConditionOperand[IdentifierT_co],
        Literal["lt"],
        Union[Constant, OtherIdentifierT_co, Operation[OtherIdentifierT_co]],
        None,
    ]:
        return ComparisonCondition(
            subject=self._operation_operand,
            operator="lt",
            target=convert_to_operand(other),
        )

    @override
    # The signature is not compatible with `object.__ne__()` on purpose.
    def __ne__(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Condition[
        NonConstantNonConditionOperand[IdentifierT_co],
        Literal["ne"],
        Union[Constant, OtherIdentifierT_co, Operation[OtherIdentifierT_co]],
        None,
    ]:
        assert other is not None, "Use `~isnull()` instead."
        return ComparisonCondition(
            subject=self._operation_operand,
            operator="ne",
            target=convert_to_operand(other),
        )

    def __add__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Operation[Union[IdentifierT_co, OtherIdentifierT_co]]:
        return ArithmeticOperation(
            operands=(self._operation_operand, convert_to_operand(other)),
            operator="add",
        )

    def __radd__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Operation[Union[IdentifierT_co, OtherIdentifierT_co]]:
        return ArithmeticOperation(
            operands=(convert_to_operand(other), self._operation_operand),
            operator="add",
        )

    def __floordiv__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Operation[Union[IdentifierT_co, OtherIdentifierT_co]]:
        return ArithmeticOperation(
            operands=(self._operation_operand, convert_to_operand(other)),
            operator="floordiv",
        )

    def __rfloordiv__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Operation[Union[IdentifierT_co, OtherIdentifierT_co]]:
        return ArithmeticOperation(
            operands=(convert_to_operand(other), self._operation_operand),
            operator="floordiv",
        )

    def __mod__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Operation[Union[IdentifierT_co, OtherIdentifierT_co]]:
        return ArithmeticOperation(
            operands=(self._operation_operand, convert_to_operand(other)),
            operator="mod",
        )

    def __rmod__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Operation[Union[IdentifierT_co, OtherIdentifierT_co]]:
        return ArithmeticOperation(
            operands=(convert_to_operand(other), self._operation_operand),
            operator="mod",
        )

    def __mul__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Operation[Union[IdentifierT_co, OtherIdentifierT_co]]:
        return ArithmeticOperation(
            operands=(self._operation_operand, convert_to_operand(other)),
            operator="mul",
        )

    def __rmul__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Operation[Union[IdentifierT_co, OtherIdentifierT_co]]:
        return ArithmeticOperation(
            operands=(convert_to_operand(other), self._operation_operand),
            operator="mul",
        )

    def __neg__(
        self,
    ) -> Operation[IdentifierT_co]:
        return ArithmeticOperation(operands=(self._operation_operand,), operator="neg")

    def __pow__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Operation[Union[IdentifierT_co, OtherIdentifierT_co]]:
        return ArithmeticOperation(
            operands=(self._operation_operand, convert_to_operand(other)),
            operator="pow",
        )

    def __rpow__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Operation[Union[IdentifierT_co, OtherIdentifierT_co]]:
        return ArithmeticOperation(
            operands=(convert_to_operand(other), self._operation_operand),
            operator="pow",
        )

    def __sub__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Operation[Union[IdentifierT_co, OtherIdentifierT_co]]:
        return ArithmeticOperation(
            operands=(self._operation_operand, convert_to_operand(other)),
            operator="sub",
        )

    def __rsub__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Operation[Union[IdentifierT_co, OtherIdentifierT_co]]:
        return ArithmeticOperation(
            operands=(convert_to_operand(other), self._operation_operand),
            operator="sub",
        )

    def __truediv__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Operation[Union[IdentifierT_co, OtherIdentifierT_co]]:
        return ArithmeticOperation(
            operands=(self._operation_operand, convert_to_operand(other)),
            operator="truediv",
        )

    def __rtruediv__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Operation[Union[IdentifierT_co, OtherIdentifierT_co]]:
        return ArithmeticOperation(
            operands=(convert_to_operand(other), self._operation_operand),
            operator="truediv",
        )


OperandConvertibleBound = OperandConvertible[Identifier]


class _BaseOperation(ABC):
    """An operation is made out of one or more operands and possibly some other primitive attributes such as strings or numbers.

    To ensure that operations are immutable and serializable, operands must never be of type `ConstantValue` or `HasIdentifier`.
    These must be converted to `Constant` and `Identifier` instead.

    This base class' sole purpose is to provide a shared fundation for `Condition` and `Operation`.
    All classes inheriting from `_BaseOperation` must inherit from one of these two classes.
    As such, this class must remain private and not referenced outside this file.
    """

    @property
    @abstractmethod
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        """The set of types of the identifiers used in this operation.

        This is used, for instance, to detect whether an operation is purely column-based and could thus be the input of a UDAF.
        """

    @classmethod
    def _get_identifier_types(
        cls, operand: Optional[Operand[Identifier]], /
    ) -> frozenset[type[Identifier]]:
        if operand is None or isinstance(operand, Constant):
            return frozenset()
        if isinstance(operand, Identifier):
            return frozenset([type(operand)])
        return operand._identifier_types


class Operation(
    OperandConvertible[IdentifierT_co],
    _BaseOperation,
):
    @property
    @override
    def _operation_operand(self) -> Operation[IdentifierT_co]:
        return self


OperationBound = Operation[Identifier]

# The following classes can be constructed from any `OperandConvertible` using Python's built-in operators.
# Because overriding these operators requires to implement methods on `OperandConvertible` instantiating the classes below, they all have to be declared in the same file to avoid circular imports.


ConditionSubjectBound = Union[Identifier, OperationBound]
ConditionSubjectT_co = TypeVar(
    "ConditionSubjectT_co", bound=ConditionSubjectBound, covariant=True
)

ConditionComparisonOperatorBound = Literal[ComparisonOperator, "isin"]
ConditionComparisonOperatorT_co = TypeVar(
    "ConditionComparisonOperatorT_co",
    bound=ConditionComparisonOperatorBound,
    covariant=True,
)

ConditionTargetBound = Optional[Union[Constant, Identifier, OperationBound]]
ConditionTargetT_co = TypeVar(
    "ConditionTargetT_co", bound=ConditionTargetBound, covariant=True
)

ConditionCombinationOperatorBound = Optional[BooleanOperator]
ConditionCombinationOperatorT_co = TypeVar(
    "ConditionCombinationOperatorT_co",
    bound=ConditionCombinationOperatorBound,
    covariant=True,
)

_OtherConditionSubjectT_co = TypeVar(
    "_OtherConditionSubjectT_co", bound=ConditionSubjectBound, covariant=True
)
_OtherConditionComparisonOperatorT_co = TypeVar(
    "_OtherConditionComparisonOperatorT_co",
    bound=ConditionComparisonOperatorBound,
    covariant=True,
)
_OtherConditionTargetT_co = TypeVar(
    "_OtherConditionTargetT_co", bound=ConditionTargetBound, covariant=True
)
_OtherConditionCombinationOperatorT_co = TypeVar(
    "_OtherConditionCombinationOperatorT_co",
    bound=ConditionCombinationOperatorBound,
    covariant=True,
)


class Condition(
    Generic[
        ConditionSubjectT_co,
        ConditionComparisonOperatorT_co,
        ConditionTargetT_co,
        ConditionCombinationOperatorT_co,
    ],
    _BaseOperation,
    ABC,
):
    def __and__(
        self,
        other: Condition[
            _OtherConditionSubjectT_co,
            _OtherConditionComparisonOperatorT_co,
            _OtherConditionTargetT_co,
            _OtherConditionCombinationOperatorT_co,
        ],
        /,
    ) -> CombinedCondition[
        Union[ConditionSubjectT_co, _OtherConditionSubjectT_co],
        Union[ConditionComparisonOperatorT_co, _OtherConditionComparisonOperatorT_co],
        Union[ConditionTargetT_co, _OtherConditionTargetT_co],
        Union[
            Literal["and"],
            ConditionCombinationOperatorT_co,
            _OtherConditionCombinationOperatorT_co,
        ],
    ]:
        return CombinedCondition(sub_conditions=(self, other), operator="and")

    def __bool__(self) -> NoReturn:
        raise AssertionError(
            "Conditions cannot be cast to a boolean as they are only evaluated during query execution. To combine conditions, use the bitwise `&`, `|`, or `~` operators."
        )

    @abstractmethod
    def __invert__(
        self,
    ) -> Condition[
        ConditionSubjectT_co,
        ConditionComparisonOperatorBound,
        ConditionTargetT_co,
        ConditionCombinationOperatorBound,
    ]: ...

    def __or__(
        self,
        other: Condition[
            _OtherConditionSubjectT_co,
            _OtherConditionComparisonOperatorT_co,
            _OtherConditionTargetT_co,
            _OtherConditionCombinationOperatorT_co,
        ],
        /,
    ) -> CombinedCondition[
        Union[ConditionSubjectT_co, _OtherConditionSubjectT_co],
        Union[ConditionComparisonOperatorT_co, _OtherConditionComparisonOperatorT_co],
        Union[ConditionTargetT_co, _OtherConditionTargetT_co],
        Union[
            Literal["or"],
            ConditionCombinationOperatorT_co,
            _OtherConditionCombinationOperatorT_co,
        ],
    ]:
        return CombinedCondition(sub_conditions=(self, other), operator="or")

    def __xor__(
        self,
        other: Condition[
            _OtherConditionSubjectT_co,
            _OtherConditionComparisonOperatorT_co,
            _OtherConditionTargetT_co,
            _OtherConditionCombinationOperatorT_co,
        ],
        /,
    ) -> NoReturn:
        raise AssertionError("Conditions cannot be `xor`ed.")

    @abstractmethod
    @override
    def __repr__(self) -> str: ...


ConditionBound = Condition[
    ConditionSubjectBound,
    ConditionComparisonOperatorBound,
    ConditionTargetBound,
    ConditionCombinationOperatorBound,
]


@keyword_only_dataclass
@dataclass(frozen=True)
class CombinedCondition(
    Condition[
        ConditionSubjectT_co,
        ConditionComparisonOperatorT_co,
        ConditionTargetT_co,
        ConditionCombinationOperatorT_co,
    ]
):
    sub_conditions: tuple[
        Condition[
            ConditionSubjectT_co,
            ConditionComparisonOperatorT_co,
            ConditionTargetT_co,
            ConditionCombinationOperatorT_co,
        ],
        Condition[
            ConditionSubjectT_co,
            ConditionComparisonOperatorT_co,
            ConditionTargetT_co,
            ConditionCombinationOperatorT_co,
        ],
    ]
    operator: ConditionCombinationOperatorT_co

    def __post_init__(self) -> None:
        # Access the `boolean_operator` property to trigger the validation process.
        assert self.boolean_operator

    @property
    def boolean_operator(self) -> BooleanOperator:
        operator: Optional[BooleanOperator] = self.operator

        assert operator is not None, "Missing combination operator."

        return operator

    @override
    def __invert__(
        self,
    ) -> Condition[
        ConditionSubjectT_co,
        ConditionComparisonOperatorBound,
        ConditionTargetT_co,
        ConditionCombinationOperatorBound,
    ]:
        return CombinedCondition(
            sub_conditions=(~self.sub_conditions[0], ~self.sub_conditions[1]),
            operator="or" if self.operator == "and" else "and",
        )

    @property
    @override
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        return frozenset(
            chain(
                *(
                    sub_condition._identifier_types
                    for sub_condition in self.sub_conditions
                )
            )
        )

    @override
    def __repr__(self) -> str:
        return f"({self.sub_conditions[0]!r}) {'&' if self.operator == 'and' else '|'} ({self.sub_conditions[1]!r})"


_ComparisonOperatorT_co = TypeVar(
    "_ComparisonOperatorT_co",
    bound=ComparisonOperator,
    covariant=True,
)

_COMPARISON_OPERATOR_TO_SYMBOL: Mapping[ComparisonOperator, str] = {
    "eq": "==",
    "ge": ">=",
    "gt": ">",
    "le": "<=",
    "lt": "<",
    "ne": "!=",
}


@keyword_only_dataclass
@dataclass(frozen=True)
class ComparisonCondition(
    Condition[ConditionSubjectT_co, _ComparisonOperatorT_co, ConditionTargetT_co, None]
):
    subject: ConditionSubjectT_co
    operator: _ComparisonOperatorT_co
    target: ConditionTargetT_co

    def __post_init__(self) -> None:
        assert not isinstance(
            self.subject, HierarchyIdentifier
        ), "Conditions on hierarchies must use `HierarchyIsinCondition`."

        if self.target is None and self.operator not in {"eq", "ne"}:
            raise ValueError(
                f"Expected `{self.target}` to be compared with an equality operator but got operator `{self.operator}`."
            )

    @property
    @override
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        return frozenset(
            chain(
                *(
                    self._get_identifier_types(operand)
                    for operand in [self.subject, self.target]
                )
            )
        )

    @override
    def __invert__(
        self,
    ) -> Condition[ConditionSubjectT_co, ComparisonOperator, ConditionTargetT_co, None]:
        return ComparisonCondition(
            subject=self.subject,
            operator=OPERATOR_TO_INVERSE_OPERATOR[self.operator],
            target=self.target,
        )

    @override
    def __repr__(self) -> str:
        return f"{self.subject!r} {_COMPARISON_OPERATOR_TO_SYMBOL[self.operator]} {self.target.value if isinstance(self.target, Constant) else self.target!r}"


_ARITHMETIC_OPERATOR_TO_SYMBOL: Mapping[ArithmeticOperator, str] = {
    "add": "+",
    "floordiv": "//",
    "mod": "%",
    "mul": "*",
    "pow": "**",
    "sub": "-",
    "truediv": "/",
}


@keyword_only_dataclass
@dataclass(eq=False, frozen=True)
class ArithmeticOperation(Operation[IdentifierT_co]):
    operands: tuple[NonConditionOperand[IdentifierT_co], ...]
    operator: ArithmeticOperator

    @property
    @override
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        return frozenset(
            chain(*(self._get_identifier_types(operand) for operand in self.operands))
        )

    @override
    def __repr__(self) -> str:
        if self.operator == "neg":
            return f"-{self._repr_operand(0)}"

        return f"{self._repr_operand(0)} {_ARITHMETIC_OPERATOR_TO_SYMBOL[self.operator]} {self._repr_operand(1)}"

    def _repr_operand(self, index: int, /) -> str:
        operand = self.operands[index]
        operand_representation = repr(operand)
        operation_is_function_call_result = not isinstance(
            operand, (ArithmeticOperation, Condition, IndexingOperation)
        )
        return (
            operand_representation
            if operation_is_function_call_result
            else f"({operand_representation})"
        )


@keyword_only_dataclass
@dataclass(eq=False, frozen=True)
class IndexingOperation(Operation[IdentifierT_co]):
    operand: NonConstantNonConditionOperand[IdentifierT_co]
    index: Union[
        Constant,
        slice,
        IdentifierT_co,
        Operation[IdentifierT_co],
    ]

    def __post_init__(self) -> None:
        allowed_data_types: tuple[DataType, ...] = ("int", "int[]", "long", "long[]")

        if (
            isinstance(self.index, Constant)
            and self.index.data_type not in allowed_data_types
        ):
            raise TypeError(
                f"Expected constant index's type to be one of `{allowed_data_types}` but got `{self.index.data_type}`."
            )

    @property
    @override
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        return self._get_identifier_types(self.operand).union(
            frozenset([])
            if isinstance(self.index, (int, tuple, slice))
            else self._get_identifier_types(self.index)
        )

    @override
    def __repr__(self) -> str:
        return f"{self.operand!r}[{self.index!r}]"


NonConstantNonConditionOperand = Union[IdentifierT_co, Operation[IdentifierT_co]]
NonConditionOperand = Union[Constant, NonConstantNonConditionOperand[IdentifierT_co]]

OperandCondition = Condition[
    NonConstantNonConditionOperand[IdentifierT_co],
    ConditionComparisonOperatorBound,
    Optional[NonConditionOperand[IdentifierT_co]],
    ConditionCombinationOperatorBound,
]

NonConstantOperand = Union[
    NonConstantNonConditionOperand[IdentifierT_co], OperandCondition[IdentifierT_co]
]
Operand = Union[Constant, NonConstantOperand[IdentifierT_co]]
