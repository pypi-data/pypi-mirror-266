from collections.abc import Mapping
from typing import Union

IPythonKeyCompletions = list[Union[str, tuple[str, str]]]


def get_ipython_key_completions_for_mapping(
    mapping: Union[Mapping[str, object], Mapping[tuple[str, ...], object]],
) -> IPythonKeyCompletions:
    """Return IPython key completions for mapping."""
    return sorted({key if isinstance(key, str) else key[-1] for key in mapping})
