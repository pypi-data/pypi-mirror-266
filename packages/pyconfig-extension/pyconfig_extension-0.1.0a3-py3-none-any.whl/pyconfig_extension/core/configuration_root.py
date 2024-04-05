from pyconfig_extension.abstracts.iconfiguration import IConfigurationSection
from pyconfig_extension.abstracts.iconfiguration_provider import IConfigurationProvider
from pyconfig_extension.abstracts.iconfiguration_root import IConfigurationRoot
import pyconfig_extension.core._internal_configuration_root_extensions as ext
from pyconfig_extension.core.configuration_section import ConfigurationSection


class ConfigurationRoot(IConfigurationRoot):
    def __init__(self, providers: list[IConfigurationProvider]):
        self.__providers = providers
        for p in providers:
            p.load()

    def reload(self):
        for provider in self.__providers:
            provider.load()

    @property
    def providers(self) -> list[IConfigurationProvider]:
        return self.__providers

    def __getitem__(self, item: str) -> str:
        return self.get_configuration(self.providers, item)

    def __setitem__(self, key: str, value: str):
        self.set_configuration(self.providers, key, value)

    def get_section(self, key) -> IConfigurationSection:
        return ConfigurationSection(self, key)

    def get_children(self) -> list[IConfigurationSection]:
        return ext.get_children_implementation(self, None)

    @staticmethod
    def get_configuration(providers: list[IConfigurationProvider], key: str) -> str | None:
        for provider in providers[::-1]:
            checked, value = provider.try_get(key)
            if checked:
                return value
        return None

    @staticmethod
    def set_configuration(providers: list[IConfigurationProvider], key: str, value: str | None):
        if len(providers) == 0:
            raise Exception("There is no source for set configuration")

        for provider in providers:
            provider.set(key, value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for provider in self.__providers:
            if hasattr(provider, "__exit__"):
                provider.__exit__(exc_type, exc_val, exc_tb)
