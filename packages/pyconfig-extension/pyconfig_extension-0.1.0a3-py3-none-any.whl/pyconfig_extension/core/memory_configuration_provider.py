from pyconfig_extension.core.configuration_provider import ConfigurationProvider
from pyconfig_extension.core.memory_configuration_source import MemoryConfigurationSource


class MemoryConfigurationProvider(ConfigurationProvider):
    def __init__(self, source: MemoryConfigurationSource):
        super().__init__()
        self.__source = source
        if self.__source.initial_data is not None:
            for key in self.__source.initial_data:
                self._data[key] = self.__source.initial_data[key]

