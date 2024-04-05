from pyconfig_extension.abstracts.iconfiguration_builder import IConfigurationBuilder, IConfigurationSource
from pyconfig_extension.abstracts.iconfiguration_provider import IConfigurationProvider


class MemoryConfigurationSource(IConfigurationSource):

    def __init__(self, initial_data: dict[str, str] | None = None):
        self.__initial_date: dict[str, str] | None = None
        if initial_data is not None:
            self.__initial_date = initial_data

    @property
    def initial_data(self) -> dict[str, str] | None:
        return self.__initial_date

    @initial_data.setter
    def initial_data(self, value: dict[str, str] | None):
        self.__initial_date = value

    def build(self, builder: IConfigurationBuilder) -> IConfigurationProvider:
        from pyconfig_extension.core.memory_configuration_provider import MemoryConfigurationProvider
        return MemoryConfigurationProvider(self)
