from collections.abc import Mapping
from typing import TypeVar

from typing_extensions import override

from .base_cube import BaseCubeBound
from .repr_json import ReprJson, ReprJsonable

CubeT_co = TypeVar("CubeT_co", bound=BaseCubeBound, covariant=True)


class BaseCubes(Mapping[str, CubeT_co], ReprJsonable):
    @override
    def _repr_json_(self) -> ReprJson:
        """Return the JSON representation of cubes."""
        return (
            {name: cube._repr_json_()[0] for name, cube in sorted(self.items())},
            {"expanded": False, "root": "Cubes"},
        )


BaseCubesBound = BaseCubes[BaseCubeBound]
