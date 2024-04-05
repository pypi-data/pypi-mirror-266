from multipledispatch import dispatch

from pyconfig_extension import guard
from pyconfig_extension.abstracts.iconfiguration import IConfiguration
from pyconfig_extension.abstracts.iconfiguration_provider import IConfigurationProvider
from pyconfig_extension.core.chained_configuration_source import ChainedConfigurationSource


class ChainedConfigurationProvider(IConfigurationProvider):

    def __init__(self, source: ChainedConfigurationSource):
        guard.check_none(source.configuration)
        self._config = source.configuration
        self._should_exit_config = source.should_exit_configuration

    @property
    def configuration(self) -> IConfiguration:
        """
        Gets the chained configuration.
        """
        return self._config

    def try_get(self, key: str) -> tuple[bool, str | None]:
        value = self._config[key]
        return value is not None, value

    def set(self, key: str, value: str):
        self._config[key] = value

    def load(self):
        pass

    def get_child_keys(self, earlier_keys: list[str], parent_path: str | None) -> list[str]:
        section: IConfiguration = self._config if parent_path is None else self._config.get_section(parent_path)

        keys: list[str] = []
        for child in section.get_children():
            keys.append(child.key)

        keys.extend(earlier_keys)
        keys.sort(key=lambda x: x.lower())
        return keys

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._should_exit_config:
            if hasattr(self._config, "__exit__"):
                self._config.__exit__(exc_type, exc_val, exc_tb)
