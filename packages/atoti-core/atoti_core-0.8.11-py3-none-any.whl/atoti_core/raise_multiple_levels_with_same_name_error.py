from collections.abc import Collection
from typing import NoReturn, Union

from .base_hierarchy import BaseHierarchyBound
from .hierarchy_identifier import HierarchyIdentifier


def raise_multiple_levels_with_same_name_error(
    level_name: str,
    *,
    hierarchies: Union[Collection[HierarchyIdentifier], Collection[BaseHierarchyBound]],
) -> NoReturn:
    raise KeyError(
        f"""Multiple levels are named {level_name}. Specify the hierarchy (and the dimension if necessary): {", ".join([
            f'cube.levels["{hierarchy.dimension_name}", "{hierarchy.hierarchy_name}", "{level_name}"]' if isinstance(hierarchy, HierarchyIdentifier) else f'cube.levels["{hierarchy.dimension}", "{hierarchy.name}", "{level_name}"]'
            for hierarchy in hierarchies
        ])}"""
    )
