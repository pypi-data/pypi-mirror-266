from __future__ import annotations

from typing import Literal

from typing_extensions import override

from .constant import Constant, ConstantValue
from .isin_condition import IsinCondition
from .level_identifier import LevelIdentifier
from .operand_convertible_with_identifier import OperandConvertibleWithIdentifier
from .operation import ComparisonCondition, Condition
from .repr_json import ReprJsonable


class BaseLevel(
    OperandConvertibleWithIdentifier[LevelIdentifier],
    ReprJsonable,
):
    def __init__(self, identifier: LevelIdentifier, /) -> None:
        super().__init__()

        self.__identifier = identifier

    @property
    def name(self) -> str:
        """Name of the level."""
        return self._identifier.level_name

    @property
    def dimension(self) -> str:
        """Name of the dimension holding the level."""
        return self._identifier.hierarchy_identifier.dimension_name

    @property
    def hierarchy(self) -> str:
        """Name of the hierarchy holding the level."""
        return self._identifier.hierarchy_identifier.hierarchy_name

    @property
    @override
    def _identifier(self) -> LevelIdentifier:
        return self.__identifier

    @property
    @override
    def _operation_operand(self) -> LevelIdentifier:
        return self._identifier

    def isin(
        self, *members: ConstantValue
    ) -> Condition[LevelIdentifier, Literal["isin"], Constant, None]:
        """Return a condition to check that the level is on one of the given members.

        ``level.isin(a, b)`` is equivalent to ``(level == a) | (level == b)``.

        Args:
            members: One or more members on which the level should be.

        Example:
            .. doctest:: Level.isin

                >>> df = pd.DataFrame(
                ...     columns=["City", "Price"],
                ...     data=[
                ...         ("Berlin", 150.0),
                ...         ("London", 240.0),
                ...         ("New York", 270.0),
                ...         ("Paris", 200.0),
                ...     ],
                ... )
                >>> table = session.read_pandas(df, keys=["City"], table_name="isin example")
                >>> cube = session.create_cube(table)
                >>> l, m = cube.levels, cube.measures
                >>> m["Price.SUM in London and Paris"] = tt.filter(
                ...     m["Price.SUM"], l["City"].isin("London", "Paris")
                ... )
                >>> cube.query(
                ...     m["Price.SUM"],
                ...     m["Price.SUM in London and Paris"],
                ...     levels=[l["City"]],
                ... )
                         Price.SUM Price.SUM in London and Paris
                City
                Berlin      150.00
                London      240.00                        240.00
                New York    270.00
                Paris       200.00                        200.00

            .. doctest:: Level.isin
                :hide:

                Clear the session to isolate the multiple methods sharing this docstring.
                >>> session._clear()

        """
        return IsinCondition(
            subject=self._operation_operand,
            elements=tuple(Constant(member) for member in members),
        )

    @override
    def isnull(
        self,
    ) -> Condition[LevelIdentifier, Literal["eq"], None, None]:
        """Return a condition evaluating to ``True`` when a level is not expressed in a query and ``False`` otherwise.

        Use `~level.isnull()` for the opposite behavior.

        Example:
            >>> df = pd.DataFrame(
            ...     columns=["Country", "City", "Price"],
            ...     data=[
            ...         ("France", "Paris", 200.0),
            ...         ("Germany", "Berlin", 120),
            ...     ],
            ... )
            >>> table = session.read_pandas(df, table_name="isnull example")
            >>> cube = session.create_cube(table)
            >>> l, m = cube.levels, cube.measures
            >>> m["City.isnull"] = l["City"].isnull()
            >>> m["City.notnull"] = ~l["City"].isnull()
            >>> cube.query(
            ...     m["City.isnull"],
            ...     m["City.notnull"],
            ...     levels=[l["Country"], l["City"]],
            ...     include_totals=True,
            ... )
                           City.isnull City.notnull
            Country City
            Total                 True        False
            France                True        False
                    Paris        False         True
            Germany               True        False
                    Berlin       False         True

        """
        return ComparisonCondition(
            subject=self._operation_operand,
            operator="eq",
            target=None,
        )
