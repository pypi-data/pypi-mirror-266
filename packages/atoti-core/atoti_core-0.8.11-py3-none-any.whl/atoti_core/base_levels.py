from __future__ import annotations

import operator
from abc import abstractmethod
from collections.abc import Iterator, Mapping
from itertools import chain
from typing import Generic, Optional, TypeVar, cast

from typing_extensions import override

from .base_hierarchies import BaseHierarchiesBound
from .base_hierarchy import LevelT_co
from .base_level import BaseLevel
from .ipython_key_completions import (
    IPythonKeyCompletions,
    get_ipython_key_completions_for_mapping,
)
from .level_key import LevelKey
from .repr_json import ReprJson, ReprJsonable

HierarchiesT_co = TypeVar("HierarchiesT_co", bound=BaseHierarchiesBound, covariant=True)


class BaseLevels(
    Generic[HierarchiesT_co, LevelT_co], Mapping[LevelKey, LevelT_co], ReprJsonable
):
    """Base class to manipulate flattened levels."""

    def __init__(self, *, hierarchies: HierarchiesT_co) -> None:
        super().__init__()

        self._hierarchies = hierarchies

    def _flatten(self) -> dict[str, Optional[LevelT_co]]:
        flat_levels: dict[str, Optional[LevelT_co]] = {}
        for hierarchy in self._hierarchies.values():
            for level in hierarchy.levels.values():
                if level.name in flat_levels:
                    # None is used as a flag to mark levels appearing in multiple hierarchies.
                    # When it happens, the user must use a tuple to retrieve the level.
                    # Like that: (hierarchy name, level name).
                    flat_levels[level.name] = None
                else:
                    flat_levels[level.name] = level  # type: ignore[assignment] # pyright: ignore[reportArgumentType]
        return flat_levels

    @override
    def __getitem__(self, key: LevelKey, /) -> LevelT_co:
        """Return the level with the given key."""
        if isinstance(key, str):
            return self._find_level(key)

        if len(key) == 2:  # noqa: PLR2004
            return self._find_level(key[1], hierarchy_name=key[0])

        # Pyright narrows the type after the previous checks but mypy does not so casting is required.
        # See https://github.com/python/mypy/issues/1178.
        key = cast(tuple[str, str, str], key)  # pyright: ignore[reportUnnecessaryCast]
        return self._find_level(key[2], dimension_name=key[0], hierarchy_name=key[1])

    @abstractmethod
    def _find_level(
        self,
        level_name: str,
        *,
        dimension_name: Optional[str] = None,
        hierarchy_name: Optional[str] = None,
    ) -> LevelT_co:
        """Get a level from the hierarchy name and level name."""

    @override
    def __iter__(
        self,
    ) -> Iterator[LevelKey]:
        """Return the iterator on all the levels."""
        return chain(
            *[
                iter(
                    {
                        (hierarchy.dimension, hierarchy.name, level_name): level
                        for level_name, level in hierarchy.levels.items()
                    }
                )
                for hierarchy in self._hierarchies.values()
            ]
        )

    @override
    def __len__(self) -> int:
        """Return the number of levels."""
        return sum(len(hierarchy.levels) for hierarchy in self._hierarchies.values())

    def _ipython_key_completions_(self) -> IPythonKeyCompletions:
        return get_ipython_key_completions_for_mapping(self._flatten())

    @override
    def _repr_json_(self) -> ReprJson:
        # Use the dimension/hierarchy/level in the map key to make it unique.
        data = {
            f"{level.name} ({level.dimension}/{level.hierarchy}/{level.name})": level._repr_json_()[
                0
            ]
            for hierarchy in self._hierarchies.values()
            for level in hierarchy.levels.values()
        }
        sorted_data = dict(sorted(data.items(), key=operator.itemgetter(0)))
        return (
            sorted_data,
            {
                "expanded": True,
                "root": "Levels",
            },
        )


BaseLevelsBound = BaseLevels[BaseHierarchiesBound, BaseLevel]
