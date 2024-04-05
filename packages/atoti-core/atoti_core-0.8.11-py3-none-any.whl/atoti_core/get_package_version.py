from importlib.metadata import version

from .get_top_level_package_name import get_top_level_package_name


def get_package_version(module_name: str) -> str:
    """Return the version of the package where *module_name* is the ``__name__`` of one of its modules."""
    package_name = get_top_level_package_name(module_name)
    return version(package_name)
