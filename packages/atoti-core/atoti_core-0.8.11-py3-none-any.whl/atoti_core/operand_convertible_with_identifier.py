from __future__ import annotations

from typing import Literal, Union, overload

from typing_extensions import override

from ._other_identifier import OtherIdentifierT_co
from .constant import Constant, ConstantValue
from .has_identifier import HasIdentifier, IdentifierT_co
from .operation import (
    ComparisonCondition,
    Condition,
    OperandConvertible,
    Operation,
    convert_to_operand,
)


class OperandConvertibleWithIdentifier(
    OperandConvertible[IdentifierT_co],
    HasIdentifier[IdentifierT_co],
):
    """This class overrides `OperandConvertible`'s `Condition`-creating methods so that the type of the returned `Condition`'s `subject` is narrowed down to an instance of `Identifier` instead of a `Union[Identifier, Operation]`.

    The returned `Condition`'s `target` is also kept as narrow as possible thanks to `@overload`s.
    """

    # Without this, the classes inheriting from this class are considered unhashable.
    @override
    def __hash__(self) -> int:
        return super().__hash__()

    @override
    def isnull(
        self,
    ) -> Condition[IdentifierT_co, Literal["eq"], None, None]:
        return ComparisonCondition(
            subject=self._operation_operand,
            operator="eq",
            target=None,
        )

    @property
    @override
    def _operation_operand(self) -> IdentifierT_co:
        return self._identifier

    # The signature is not compatible with `object.__eq__()` on purpose.
    @overload  # type: ignore[override]
    def __eq__(
        self, other: ConstantValue, /
    ) -> Condition[IdentifierT_co, Literal["eq"], Constant, None]: ...

    @overload
    def __eq__(
        self, other: HasIdentifier[OtherIdentifierT_co], /
    ) -> Condition[IdentifierT_co, Literal["eq"], OtherIdentifierT_co, None]: ...

    @overload
    def __eq__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Condition[
        IdentifierT_co,
        Literal["eq"],
        Union[Constant, OtherIdentifierT_co, Operation[OtherIdentifierT_co]],
        None,
    ]: ...

    @override
    # The signature is not compatible with `object.__eq__()` on purpose.
    def __eq__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Condition[
        IdentifierT_co,
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

    @overload
    def __ge__(
        self, other: ConstantValue, /
    ) -> Condition[IdentifierT_co, Literal["ge"], Constant, None]: ...

    @overload
    def __ge__(
        self, other: HasIdentifier[OtherIdentifierT_co], /
    ) -> Condition[IdentifierT_co, Literal["ge"], OtherIdentifierT_co, None]: ...

    @overload
    def __ge__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Condition[
        IdentifierT_co,
        Literal["ge"],
        Union[Constant, OtherIdentifierT_co, Operation[OtherIdentifierT_co]],
        None,
    ]: ...

    @override
    def __ge__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Condition[
        IdentifierT_co,
        Literal["ge"],
        Union[Constant, OtherIdentifierT_co, Operation[OtherIdentifierT_co]],
        None,
    ]:
        return ComparisonCondition(
            subject=self._operation_operand,
            operator="ge",
            target=convert_to_operand(other),
        )

    @overload
    def __gt__(
        self, other: ConstantValue, /
    ) -> Condition[IdentifierT_co, Literal["gt"], Constant, None]: ...

    @overload
    def __gt__(
        self, other: HasIdentifier[OtherIdentifierT_co], /
    ) -> Condition[IdentifierT_co, Literal["gt"], OtherIdentifierT_co, None]: ...

    @overload
    def __gt__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Condition[
        IdentifierT_co,
        Literal["gt"],
        Union[Constant, OtherIdentifierT_co, Operation[OtherIdentifierT_co]],
        None,
    ]: ...

    @override
    def __gt__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Condition[
        IdentifierT_co,
        Literal["gt"],
        Union[Constant, OtherIdentifierT_co, Operation[OtherIdentifierT_co]],
        None,
    ]:
        return ComparisonCondition(
            subject=self._operation_operand,
            operator="gt",
            target=convert_to_operand(other),
        )

    @overload
    def __le__(
        self, other: ConstantValue, /
    ) -> Condition[IdentifierT_co, Literal["le"], Constant, None]: ...

    @overload
    def __le__(
        self, other: HasIdentifier[OtherIdentifierT_co], /
    ) -> Condition[IdentifierT_co, Literal["le"], OtherIdentifierT_co, None]: ...

    @overload
    def __le__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Condition[
        IdentifierT_co,
        Literal["le"],
        Union[Constant, OtherIdentifierT_co, Operation[OtherIdentifierT_co]],
        None,
    ]: ...

    @override
    def __le__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Condition[
        IdentifierT_co,
        Literal["le"],
        Union[Constant, OtherIdentifierT_co, Operation[OtherIdentifierT_co]],
        None,
    ]:
        return ComparisonCondition(
            subject=self._operation_operand,
            operator="le",
            target=convert_to_operand(other),
        )

    @overload
    def __lt__(
        self, other: ConstantValue, /
    ) -> Condition[IdentifierT_co, Literal["lt"], Constant, None]: ...

    @overload
    def __lt__(
        self, other: HasIdentifier[OtherIdentifierT_co], /
    ) -> Condition[IdentifierT_co, Literal["lt"], OtherIdentifierT_co, None]: ...

    @overload
    def __lt__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Condition[
        IdentifierT_co,
        Literal["lt"],
        Union[Constant, OtherIdentifierT_co, Operation[OtherIdentifierT_co]],
        None,
    ]: ...

    @override
    def __lt__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Condition[
        IdentifierT_co,
        Literal["lt"],
        Union[Constant, OtherIdentifierT_co, Operation[OtherIdentifierT_co]],
        None,
    ]:
        return ComparisonCondition(
            subject=self._operation_operand,
            operator="lt",
            target=convert_to_operand(other),
        )

    # The signature is not compatible with `object.__ne__()` on purpose.
    @overload  # type: ignore[override]
    def __ne__(
        self, other: ConstantValue, /
    ) -> Condition[IdentifierT_co, Literal["ne"], Constant, None]: ...

    @overload
    def __ne__(
        self, other: HasIdentifier[OtherIdentifierT_co], /
    ) -> Condition[IdentifierT_co, Literal["ne"], OtherIdentifierT_co, None]: ...

    @overload
    def __ne__(
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Condition[
        IdentifierT_co,
        Literal["ne"],
        Union[Constant, OtherIdentifierT_co, Operation[OtherIdentifierT_co]],
        None,
    ]: ...

    @override
    # The signature is not compatible with `object.__ne__()` on purpose.
    def __ne__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        other: Union[
            ConstantValue,
            HasIdentifier[OtherIdentifierT_co],
            Operation[OtherIdentifierT_co],
        ],
        /,
    ) -> Condition[
        IdentifierT_co,
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
