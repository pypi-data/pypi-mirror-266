from pyconfig_extension.abstracts.iconfiguration_builder import IConfigurationBuilder, IConfigurationSource
from pyconfig_extension.abstracts.iconfiguration_root import IConfigurationRoot
import pyconfig_extension.guard as guard


class ConfigurationBuilder(IConfigurationBuilder):
    def __init__(self):
        self.__properties: dict[str, object] = {}
        self.__sources: list[IConfigurationSource] = []

    @property
    def properties(self) -> dict[str, object]:
        return self.__properties

    @property
    def sources(self) -> list[IConfigurationSource]:
        return self.__sources

    def add(self, source: IConfigurationSource) -> IConfigurationBuilder:
        guard.check_none(source)

        self.sources.append(source)
        return self

    def build(self) -> IConfigurationRoot:
        providers = []
        for source in self.sources:
            provider = source.build(self)
            providers.append(provider)
        from pyconfig_extension.core.configuration_root import ConfigurationRoot
        return ConfigurationRoot(providers)
