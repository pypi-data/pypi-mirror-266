from __future__ import annotations

from abc import abstractmethod
from typing import Any, Generic, Literal, Optional, TypeVar

import pandas as pd
from typing_extensions import override

from .base_hierarchies import BaseHierarchiesBound
from .base_level import BaseLevel
from .base_levels import BaseLevelsBound, HierarchiesT_co
from .base_measure import BaseMeasure
from .base_measures import BaseMeasuresBound
from .context import Context
from .default_query_timeout import DEFAULT_QUERY_TIMEOUT
from .duration import Duration
from .frozendict import frozendict
from .query_filter import QueryFilter
from .repr_json import ReprJson, ReprJsonable
from .scenario import BASE_SCENARIO_NAME
from .sequence_or_deprecated_set import SequenceOrDeprecatedSet

LevelsT_co = TypeVar("LevelsT_co", bound=BaseLevelsBound, covariant=True)
MeasuresT_co = TypeVar("MeasuresT_co", bound=BaseMeasuresBound, covariant=True)


class BaseCube(
    Generic[HierarchiesT_co, LevelsT_co, MeasuresT_co],
    ReprJsonable,
):
    def __init__(
        self, name: str, /, *, hierarchies: HierarchiesT_co, measures: MeasuresT_co
    ) -> None:
        super().__init__()

        self._hierarchies = hierarchies
        self._measures = measures
        self._name = name

    @property
    def name(self) -> str:
        """Name of the cube."""
        return self._name

    @property
    @abstractmethod
    def levels(self) -> LevelsT_co:
        """Levels of the cube."""

    @property
    def measures(self) -> MeasuresT_co:
        """Measures of the cube."""
        return self._measures

    @property
    def hierarchies(self) -> HierarchiesT_co:
        """Hierarchies of the cube."""
        return self._hierarchies

    @abstractmethod
    def query(
        self,
        *measures: BaseMeasure,
        context: Context = frozendict(),  # noqa: B008
        filter: Optional[QueryFilter] = None,  # noqa: A002
        include_totals: bool = False,
        levels: SequenceOrDeprecatedSet[BaseLevel] = (),
        mode: Literal["pretty", "raw"] = "pretty",
        scenario: str = BASE_SCENARIO_NAME,
        timeout: Duration = DEFAULT_QUERY_TIMEOUT,
        **kwargs: Any,
    ) -> pd.DataFrame: ...

    @override
    def _repr_json_(self) -> ReprJson:
        return (
            {
                "Dimensions": self.hierarchies._repr_json_()[0],
                "Measures": self.measures._repr_json_()[0],
            },
            {"expanded": False, "root": self.name},
        )


BaseCubeBound = BaseCube[BaseHierarchiesBound, BaseLevelsBound, BaseMeasuresBound]
