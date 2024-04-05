from abc import abstractmethod, ABC

from multipledispatch import dispatch

from pyconfig_extension.abstracts.stream_configuration_source import StreamConfigurationSource
from pyconfig_extension.core.configuration_provider import ConfigurationProvider


class StreamConfigurationProvider(ConfigurationProvider, ABC):

    def __init__(self, source: StreamConfigurationSource):
        super().__init__()
        self._source = source
        self._loaded = False

    def load(self):
        if self._loaded:
            raise Exception()
        self.load_stream(self._source.stream)
        self._loaded = True

    @abstractmethod
    def load_stream(self, stream):
        raise NotImplementedError
