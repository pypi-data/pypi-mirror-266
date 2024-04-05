from __future__ import annotations

from abc import abstractmethod
from collections.abc import Mapping
from typing import Generic, Literal, TypeVar

from typing_extensions import override

from .base_level import BaseLevel
from .constant import Constant, ConstantValue
from .has_identifier import HasIdentifier
from .hierarchy_identifier import HierarchyIdentifier
from .hierarchy_isin_condition import HierarchyIsinCondition
from .operation import Condition
from .repr_json import ReprJson, ReprJsonable

LevelT_co = TypeVar("LevelT_co", bound=BaseLevel, covariant=True)


class BaseHierarchy(
    Generic[LevelT_co], HasIdentifier[HierarchyIdentifier], ReprJsonable
):
    def __init__(self, identifier: HierarchyIdentifier, /) -> None:
        super().__init__()

        self.__identifier = identifier

    @property
    def name(self) -> str:
        """Name of the hierarchy."""
        return self._identifier.hierarchy_name

    @property
    def dimension(self) -> str:
        """Name of the dimension of the hierarchy.

        A dimension is a logical group of attributes (e.g. :guilabel:`Geography`).
        It can be thought of as a folder containing hierarchies.
        """
        return self._identifier.dimension_name

    @property
    @abstractmethod
    def levels(self) -> Mapping[str, LevelT_co]:
        """Levels of the hierarchy."""

    @property
    @abstractmethod
    def slicing(self) -> bool:
        """Whether the hierarchy is slicing or not.

        * A regular (i.e. non-slicing) hierarchy is considered aggregable, meaning that it makes sense to aggregate data across all members of the hierarchy.

          For instance, for a :guilabel:`Geography` hierarchy, it is useful to see the worldwide aggregated :guilabel:`Turnover` across all countries.

        * A slicing hierarchy is not aggregable at the top level, meaning that it does not make sense to aggregate data across all members of the hierarchy.

          For instance, for an :guilabel:`As of date` hierarchy giving the current bank account :guilabel:`Balance` for a given date, it does not provide any meaningful information to aggregate the :guilabel:`Balance` across all the dates.
        """

    def isin(
        self, *member_paths: tuple[ConstantValue, ...]
    ) -> Condition[HierarchyIdentifier, Literal["isin"], Constant, None]:
        """Return a condition to check that the hierarchy is on one of the given members.

        Considering ``hierarchy_1`` containing ``level_1`` and ``level_2``, ``hierarchy_1.isin((a,), (b, c))`` is equivalent to ``(level_1 == a) | ((level_1 == b) & (level_2 == c))``.

        Args:
            member_paths: One or more member paths expressed as tuples on which the hierarchy should be.
                Each element in a tuple corresponds to a level of the hierarchy, from the shallowest to the deepest.

        Example:
            .. doctest:: Hierarchy.isin

                >>> df = pd.DataFrame(
                ...     columns=["Country", "City", "Price"],
                ...     data=[
                ...         ("Germany", "Berlin", 150.0),
                ...         ("Germany", "Hamburg", 120.0),
                ...         ("United Kingdom", "London", 240.0),
                ...         ("United States", "New York", 270.0),
                ...         ("France", "Paris", 200.0),
                ...     ],
                ... )
                >>> table = session.read_pandas(
                ...     df, keys=["Country", "City"], table_name="isin example"
                ... )
                >>> cube = session.create_cube(table)
                >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
                >>> h["Geography"] = [l["Country"], l["City"]]
                >>> m["Price.SUM in Germany and Paris"] = tt.filter(
                ...     m["Price.SUM"],
                ...     h["Geography"].isin(("Germany",), ("France", "Paris")),
                ... )
                >>> cube.query(
                ...     m["Price.SUM"],
                ...     m["Price.SUM in Germany and Paris"],
                ...     levels=[l["Geography", "City"]],
                ... )
                                        Price.SUM Price.SUM in Germany and Paris
                Country        City
                France         Paris       200.00                         200.00
                Germany        Berlin      150.00                         150.00
                               Hamburg     120.00                         120.00
                United Kingdom London      240.00
                United States  New York    270.00

            .. doctest:: Hierarchy.isin
                :hide:

                Clear the session to isolate the multiple methods sharing this docstring.
                >>> session._clear()
        """
        return HierarchyIsinCondition(
            subject=self._identifier,
            level_names=(*self.levels,),
            member_paths=tuple(
                tuple(Constant(member) for member in member_path)
                for member_path in member_paths
            ),
        )

    @override
    def _repr_json_(self) -> ReprJson:
        root = f"{self.name}{' (slicing)' if self.slicing else ''}"
        return (
            [level.name for level in self.levels.values()],
            {
                "root": root,
                "expanded": False,
            },
        )

    @property
    @override
    def _identifier(self) -> HierarchyIdentifier:
        return self.__identifier

    @override
    def __hash__(self) -> int:
        # See comment in `OperandConvertible.__hash__()`.
        return id(self)


BaseHierarchyBound = BaseHierarchy[BaseLevel]
