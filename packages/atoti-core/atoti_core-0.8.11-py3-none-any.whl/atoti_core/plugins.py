from collections.abc import Mapping

from .get_installed_plugins import get_installed_plugins
from .plugin import Plugin


class _Plugins:
    def __init__(self) -> None:
        self._default: dict[str, Plugin] = {}
        self._initialized: bool = False

    @property
    def default(self) -> Mapping[str, Plugin]:
        if not self._initialized:
            self._default.clear()
            self._default.update(get_installed_plugins())
            self._initialized = True

        return self._default

    @default.setter
    def default(self, value: Mapping[str, Plugin], /) -> None:
        assert not self._initialized, "The default plugins have already been initialized, they cannot be changed anymore."

        self._default.clear()
        self._default.update(value)
        self._initialized = True


PLUGINS = _Plugins()
