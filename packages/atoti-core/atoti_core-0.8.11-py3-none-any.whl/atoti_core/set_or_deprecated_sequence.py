from collections.abc import Set as AbstractSet
from typing import Annotated, TypeVar, Union
from warnings import warn

from pydantic import AfterValidator

from .deprecated_warning_category import DEPRECATED_WARNING_CATEGORY
from .frozen_collections import FrozenSequence

_ElementT_co = TypeVar("_ElementT_co", covariant=True)

_SetOrDeprecatedSequence = Union[
    AbstractSet[_ElementT_co], FrozenSequence[_ElementT_co]
]


def _validate(
    value: _SetOrDeprecatedSequence[_ElementT_co], /
) -> AbstractSet[_ElementT_co]:
    if isinstance(value, AbstractSet):
        return value

    warn(
        "Passing a Sequence is deprecated, pass a Set instead.",
        category=DEPRECATED_WARNING_CATEGORY,
        stacklevel=2,
    )
    return frozenset(value)


SetOrDeprecatedSequence = Annotated[
    _SetOrDeprecatedSequence[_ElementT_co],
    AfterValidator(_validate),
]
