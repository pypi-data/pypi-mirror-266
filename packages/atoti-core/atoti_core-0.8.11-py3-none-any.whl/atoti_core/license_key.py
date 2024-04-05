LICENSE_KEY_ENV_VAR_NAME = "ATOTI_LICENSE"


class _LicenseKey:
    def __init__(self) -> None:
        self._initialized = False
        self._use_env_var = True

    @property
    def use_env_var(self) -> bool:
        if not self._initialized:
            self._initialized = True

        return self._use_env_var

    @use_env_var.setter
    def use_env_var(self, value: bool, /) -> None:
        assert not self._initialized, "The default behavior has already been initialized, it cannot be changed anymore."

        self._use_env_var = value
        self._initialized = True


LICENSE_KEY = _LicenseKey()
