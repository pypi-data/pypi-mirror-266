from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable, Iterator, MutableSet, Set as AbstractSet
from typing import TypeVar

from typing_extensions import override

_Item = TypeVar("_Item")


class DelegateMutableSet(MutableSet[_Item]):
    @abstractmethod
    def _get_underlying(self) -> set[_Item]: ...

    @abstractmethod
    def _set_underlying(self, new_set: AbstractSet[_Item], /) -> None: ...

    @override
    def __contains__(self, value: object, /) -> bool:
        return value in self._get_underlying()

    @override
    def __iter__(self) -> Iterator[_Item]:
        return iter(self._get_underlying())

    @override
    def __len__(self) -> int:
        return len(self._get_underlying())

    @override
    def __repr__(self) -> str:
        return repr(self._get_underlying())

    @override
    def add(self, value: _Item) -> None:
        new_set = set(self._get_underlying())
        new_set.add(value)
        self._set_underlying(new_set)

    @override
    def clear(self) -> None:
        new_set: set[_Item] = set()
        self._set_underlying(new_set)

    @override
    def discard(self, value: _Item) -> None:
        new_set = set(self._get_underlying())
        new_set.discard(value)
        self._set_underlying(new_set)

    def update(self, *s: Iterable[_Item]) -> None:  # pylint: disable=no-iterable
        new_set = set(self._get_underlying())
        new_set.update(*s)
        self._set_underlying(new_set)
