from __future__ import annotations


class MissingPluginError(ImportError):
    def __init__(self, plugin_key: str):
        plugin_name = f"atoti-{plugin_key}"
        message = f"The `{plugin_name}` plugin is missing, install it and try again."

        super().__init__(message)
