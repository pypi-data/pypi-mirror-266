from __future__ import annotations

from abc import abstractmethod
from collections.abc import (
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    Mapping,
    MutableMapping,
    Set as AbstractSet,
    ValuesView,
)
from typing import (
    TYPE_CHECKING,
    Optional,
    TypeVar,
    Union,
    overload,
)

from typing_extensions import override

from .ipython_key_completions import (
    IPythonKeyCompletions,
    get_ipython_key_completions_for_mapping,
)

if TYPE_CHECKING:
    from _typeshed import SupportsKeysAndGetItem  # pylint: disable=nested-import

_Key = TypeVar("_Key")
_Value = TypeVar("_Value")


class DelegateMutableMapping(MutableMapping[_Key, _Value]):
    # `keys()`, `items()`, and `values()` methods are reimplemented for performance reasons.
    # See https://github.com/activeviam/atoti-python-api/pull/1162#issuecomment-592551497.

    @abstractmethod
    def _get_underlying(self) -> dict[_Key, _Value]: ...

    @abstractmethod
    def _update(self, other: Mapping[_Key, _Value], /) -> None: ...

    @abstractmethod
    def _delete_keys(self, keys: AbstractSet[_Key], /) -> None: ...

    @override
    def __delitem__(self, key: _Key, /) -> None:
        return self._delete_keys({key})

    @override
    def clear(self) -> None:
        return self._delete_keys(self.keys())

    @overload
    def update(
        self, __m: SupportsKeysAndGetItem[_Key, _Value], **kwargs: _Value
    ) -> None: ...

    @overload
    def update(self, __m: Iterable[tuple[_Key, _Value]], **kwargs: _Value) -> None:  # pylint: disable=no-iterable
        ...

    @overload
    def update(self, **kwargs: _Value) -> None: ...

    @override  # type: ignore[misc]
    # Pyright fails to see that the override is correct but mypy can see it.
    def update(  # pyright: ignore[reportInconsistentOverload]
        self,
        __m: Optional[
            Union[Mapping[_Key, _Value], Iterable[tuple[_Key, _Value]]]  # pylint: disable=no-iterable
        ] = None,
        **kwargs: _Value,
    ) -> None:
        other: dict[_Key, _Value] = {}
        if __m is not None:
            other.update(__m)
        other.update(**kwargs)
        self._update(other)

    @override
    def __setitem__(self, key: _Key, value: _Value, /) -> None:
        self.update({key: value})

    @override
    def __getitem__(self, key: _Key, /) -> _Value:
        return self._get_underlying()[key]

    @override
    def __iter__(self) -> Iterator[_Key]:
        return iter(self._get_underlying())

    @override
    def __len__(self) -> int:
        return len(self._get_underlying())

    @override
    def __repr__(self) -> str:
        return repr(self._get_underlying())

    @override
    def keys(self) -> KeysView[_Key]:
        return self._get_underlying().keys()

    @override
    def items(self) -> ItemsView[_Key, _Value]:
        return self._get_underlying().items()

    @override
    def values(self) -> ValuesView[_Value]:
        return self._get_underlying().values()

    def _ipython_key_completions_(self) -> IPythonKeyCompletions:
        return get_ipython_key_completions_for_mapping(self)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
