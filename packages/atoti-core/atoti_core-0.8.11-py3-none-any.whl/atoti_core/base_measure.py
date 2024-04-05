from abc import abstractmethod
from typing import Literal, Optional

from typing_extensions import override

from .measure_identifier import MeasureIdentifier
from .operand_convertible_with_identifier import OperandConvertibleWithIdentifier
from .operation import ComparisonCondition, Condition


class BaseMeasure(OperandConvertibleWithIdentifier[MeasureIdentifier]):
    def __init__(self, identifier: MeasureIdentifier, /) -> None:
        super().__init__()

        self.__identifier = identifier

    @property
    def name(self) -> str:
        """Name of the measure."""
        return self._identifier.measure_name

    @property
    @abstractmethod
    def folder(self) -> Optional[str]:
        """Folder of the measure."""

    @property
    @abstractmethod
    def visible(self) -> bool:
        """Whether the measure is visible or not."""

    @property
    @abstractmethod
    def description(self) -> Optional[str]:
        """Description of the measure."""

    @property
    @abstractmethod
    def formatter(self) -> Optional[str]:
        """Formatter of the measure."""

    @override
    def isnull(self) -> Condition[MeasureIdentifier, Literal["eq"], None, None]:
        """Return a condition evaluating to ``True`` if the measure evalutes to ``None`` and ``False`` otherwise.

        Use ``~measure.isnull()`` for the opposite behavior.

        Example:
            >>> df = pd.DataFrame(
            ...     columns=["Country", "City", "Price"],
            ...     data=[
            ...         ("France", "Paris", 200.0),
            ...         ("Germany", "Berlin", None),
            ...     ],
            ... )
            >>> table = session.read_pandas(df, table_name="isnull example")
            >>> cube = session.create_cube(table)
            >>> l, m = cube.levels, cube.measures
            >>> m["Price.isnull"] = m["Price.SUM"].isnull()
            >>> m["Price.notnull"] = ~m["Price.SUM"].isnull()
            >>> cube.query(
            ...     m["Price.isnull"],
            ...     m["Price.notnull"],
            ...     levels=[l["Country"]],
            ... )
                    Price.isnull Price.notnull
            Country
            France         False          True
            Germany         True         False

        """
        return ComparisonCondition(
            subject=self._operation_operand, operator="eq", target=None
        )

    @property
    @override
    def _identifier(self) -> MeasureIdentifier:
        return self.__identifier

    @property
    @override
    def _operation_operand(self) -> MeasureIdentifier:
        return self._identifier
