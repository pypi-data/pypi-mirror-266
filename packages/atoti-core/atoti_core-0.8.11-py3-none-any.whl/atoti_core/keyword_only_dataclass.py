from __future__ import annotations

from dataclasses import is_dataclass
from functools import wraps
from inspect import isclass
from typing import TypeVar

_T = TypeVar("_T")


def keyword_only_dataclass(cls: _T) -> _T:
    """Decorate a dataclass to force its construction to be done with keyword-only parameters.

    Replace with func:`dataclasses.dataclass`'s *kw_only* when bumping minimum supported version of Python to 3.10.
    """
    assert is_dataclass(cls), f"Expected a dataclass but received {cls}."
    assert isclass(cls)
    init = cls.__init__

    @wraps(init)
    def init_enforcing_keyword_only_arguments(
        self: _T, *args: object, **kwargs: object
    ) -> None:
        assert (
            len(args) == 0
        ), f"{cls.__name__} expects keyword-only arguments but the following positional arguments were passed: {args}."
        init(self, **kwargs)

    setattr(cls, "__init__", init_enforcing_keyword_only_arguments)  # noqa: B010

    return cls  # type: ignore[return-value] # pyright: ignore[reportReturnType]
