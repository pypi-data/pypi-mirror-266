from collections.abc import Sequence, Set as AbstractSet
from typing import Annotated, TypeVar, Union
from warnings import warn

from pydantic import AfterValidator

from .deprecated_warning_category import DEPRECATED_WARNING_CATEGORY
from .frozen_collections import FrozenSequence

_ElementT_co = TypeVar("_ElementT_co", covariant=True)

_SequenceOrDeprecatedSet = Union[
    FrozenSequence[_ElementT_co], AbstractSet[_ElementT_co]
]


def _validate(
    value: _SequenceOrDeprecatedSet[_ElementT_co], /
) -> Sequence[_ElementT_co]:
    if isinstance(value, Sequence):
        return value

    warn(
        "Passing a Set is deprecated, pass a Sequence instead.",
        category=DEPRECATED_WARNING_CATEGORY,
        stacklevel=2,
    )
    return tuple(value)


SequenceOrDeprecatedSet = Annotated[
    _SequenceOrDeprecatedSet[_ElementT_co],
    AfterValidator(_validate),
]
