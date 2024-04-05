import sys
from collections.abc import Mapping
from functools import cache
from importlib.metadata import version

from .get_package_version import get_package_version
from .plugin import Plugin

# https://packaging.python.org/guides/creating-and-discovering-plugins/#using-package-metadata
# The “selectable” entry points were introduced in importlib_metadata 3.6 and Python 3.10.
# Prior to those changes, entry_points accepted no parameters and always returned a dictionary of entry points.
if sys.version_info < (3, 10):
    from importlib_metadata import (  # pylint: disable=nested-import
        entry_points,
    )
else:
    from importlib.metadata import (  # pylint: disable=nested-import
        entry_points,
    )


@cache
def get_installed_plugins() -> Mapping[str, Plugin]:
    expected_version = get_package_version(__name__)
    plugins: dict[str, Plugin] = {}

    for entry_point in entry_points(group="atoti.plugins"):
        entry_point_name: str = entry_point.name
        plugin_package_name = f"atoti-{entry_point_name}"
        plugin_version = version(plugin_package_name)

        assert (
            entry_point_name == "jupyterlab3" or (plugin_version == expected_version)
        ), f"This version of Atoti only supports {plugin_package_name} v{expected_version} but got v{plugin_version}."

        plugin_class = entry_point.load()
        plugin = plugin_class()

        if not isinstance(plugin, Plugin):
            raise TypeError(f"Unexpected plugin type: {type(plugin)}.")

        plugins[entry_point_name] = plugin

    return plugins
