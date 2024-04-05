from __future__ import annotations

from abc import abstractmethod
from collections.abc import Collection, Iterator, MutableSet
from typing import Any, TypeVar

from typing_extensions import Self, override

_Item = TypeVar("_Item")


# All users of this class are on deprecated paths.
# Do not use it more.
# Delete it once the dependant deprecated paths are removed.
class ReactiveMutableSet(MutableSet[_Item]):
    def __init__(self, data: Collection[_Item], /) -> None:
        super().__init__()

        self._data = set(data)

    @abstractmethod
    def _on_change(self, *, in_place: bool) -> None:
        """Hook called each time the data in the set changes."""

    @override
    def __contains__(self, value: object) -> bool:
        return value in self._data

    @override
    def add(self, value: _Item) -> None:
        self._data.add(value)
        self._on_change(in_place=True)

    @override
    def clear(self) -> None:
        self._data.clear()
        self._on_change(in_place=True)

    @override
    def discard(self, value: _Item) -> None:
        self._data.discard(value)
        self._on_change(in_place=True)

    def update(self, *values: Collection[_Item]) -> None:
        self._data.update(*values)
        self._on_change(in_place=True)

    @override
    def __iter__(self) -> Iterator[_Item]:
        return iter(self._data)

    @override
    def __len__(self) -> int:
        return len(self._data)

    @override
    def __repr__(self) -> str:
        return repr(self._data)

    @override
    def __ior__(self, values: Any) -> Self:
        new_data = self._data.copy()
        new_data |= values
        self._data = set(new_data)
        self._on_change(in_place=False)
        return self

    @override
    def __iand__(self, values: Any) -> Self:
        new_data = self._data.copy()
        new_data &= values
        self._data = set(new_data)
        self._on_change(in_place=False)
        return self

    @override
    def __isub__(self, values: Any) -> Self:
        new_data = self._data.copy()
        new_data -= values
        self._data = set(new_data)
        self._on_change(in_place=False)
        return self

    @override
    def __ixor__(self, values: Any) -> Self:
        new_data = self._data.copy()
        new_data ^= values
        self._data = set(new_data)
        self._on_change(in_place=False)
        return self
