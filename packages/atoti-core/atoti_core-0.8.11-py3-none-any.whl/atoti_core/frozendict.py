from collections.abc import Iterator, Mapping
from typing import Any, Optional, TypeVar, overload

from typing_extensions import Never, override

from .ipython_key_completions import (
    IPythonKeyCompletions,
    get_ipython_key_completions_for_mapping,
)

_Key = TypeVar("_Key")
_Value = TypeVar("_Value")


# Consider replacing with MappingProxyType once Pydantic supports it.
# See https://github.com/pydantic/pydantic/issues/6868.
class _FrozenDict(dict[_Key, _Value]):
    """:class:`dict` raising an error in all methods allowing mutations."""

    @override
    def __hash__(self) -> int:  # type: ignore[override] # pyright: ignore[reportIncompatibleVariableOverride]
        return hash(tuple(self.items()))

    @override
    def __setitem__(self, *args: Any, **kwargs: Any) -> Never:
        self._raise_frozen_error()

    @override
    def __delitem__(self, *args: Any, **kwargs: Any) -> Never:
        self._raise_frozen_error()

    @override
    def setdefault(self, *args: Any, **kwargs: Any) -> Never:
        self._raise_frozen_error()

    @override
    def pop(self, *args: Any, **kwargs: Any) -> Never:
        self._raise_frozen_error()

    @override
    def update(self, *args: Any, **kwargs: Any) -> Never:
        self._raise_frozen_error()

    def _raise_frozen_error(self) -> Never:
        raise TypeError("The dict is frozen.")

    def _ipython_key_completions_(self) -> IPythonKeyCompletions:
        return get_ipython_key_completions_for_mapping(self)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]


class frozendict(Mapping[_Key, _Value]):  # noqa: N801
    __slots__ = ("_data",)

    @overload
    def __init__(self, /) -> None: ...

    @overload
    def __init__(self, data: Mapping[_Key, _Value], /) -> None: ...

    def __init__(self, data: Optional[Mapping[_Key, _Value]] = None, /) -> None:
        self._data = _FrozenDict() if data is None else _FrozenDict(data)

    @override
    def __getitem__(self, key: _Key, /) -> _Value:
        return self._data[key]

    @override
    def __hash__(self) -> int:
        return hash(self._data)

    @override
    def __iter__(self) -> Iterator[_Key]:
        return iter(self._data)

    @override
    def __len__(self) -> int:
        return len(self._data)

    @override
    def __repr__(self) -> str:
        return repr(dict(self))

    def _ipython_key_completions_(self) -> IPythonKeyCompletions:
        return self._data._ipython_key_completions_()
