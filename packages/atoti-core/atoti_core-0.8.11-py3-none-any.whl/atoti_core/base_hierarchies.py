from __future__ import annotations

from abc import abstractmethod
from collections import defaultdict
from collections.abc import Collection, Mapping
from typing import Optional, TypeVar, Union

from typing_extensions import override

from .base_hierarchy import BaseHierarchyBound
from .hierarchy_identifier import HierarchyIdentifier
from .hierarchy_key import HierarchyKey
from .repr_json import ReprJson, ReprJsonable

HierarchyT_co = TypeVar("HierarchyT_co", bound=BaseHierarchyBound, covariant=True)


class BaseHierarchies(Mapping[HierarchyKey, HierarchyT_co], ReprJsonable):
    """Manage the base hierarchies."""

    @abstractmethod
    @override
    def __getitem__(self, key: HierarchyKey, /) -> HierarchyT_co:
        """Return the hierarchy with the given name."""

    @override
    def _repr_json_(self) -> ReprJson:
        """Return the JSON representation of hierarchies."""
        dimensions: dict[str, list[HierarchyT_co]] = defaultdict(list)
        for hierarchy in self.values():
            dimensions[hierarchy.dimension].append(hierarchy)
        json = {
            dimension: dict(
                sorted(
                    {
                        hierarchy._repr_json_()[1]["root"]: hierarchy._repr_json_()[0]
                        for hierarchy in dimension_hierarchies
                    }.items()
                )
            )
            for dimension, dimension_hierarchies in sorted(dimensions.items())
        }
        return json, {"expanded": True, "root": "Dimensions"}

    @staticmethod
    def _convert_key(key: HierarchyKey, /) -> tuple[Optional[str], str]:
        """Get the dimension and hierarchy from the key."""
        if isinstance(key, str):
            return (None, key)

        return key

    @staticmethod
    def _multiple_hierarchies_error(
        key: HierarchyKey,
        hierarchies: Union[Collection[HierarchyT_co], Collection[HierarchyIdentifier]],
    ) -> KeyError:
        return KeyError(
            f"""Multiple hierarchies with name {key}. Specify the dimension: {", ".join([
            f'cube.hierarchies["{hierarchy.dimension_name}", "{hierarchy.dimension_name}"]'if isinstance(hierarchy, HierarchyIdentifier) else f'cube.hierarchies["{hierarchy.dimension}", "{hierarchy.name}"]'
            for hierarchy in hierarchies
        ])}"""
        )


BaseHierarchiesBound = BaseHierarchies[BaseHierarchyBound]
