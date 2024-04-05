from abc import abstractmethod

from pyconfig_extension import guard
from pyconfig_extension.core.configuration_provider import ConfigurationProvider
from pyconfig_extension.file.file_configuration_source import FileConfigurationSource


class FileConfigurationProvider(ConfigurationProvider):

    def __init__(self, source: FileConfigurationSource):
        super().__init__()
        guard.check_none(source)
        self._source = source

    @property
    def source(self) -> FileConfigurationSource:
        return self._source

    def load(self):
        if self.source.stream is not None:
            self.load_stream(self.source.stream)
        elif self.source.path is not None and self.source.stream is None:
            try:
                with open(self.source.path, "r") as f:
                    content = f.read()
                    self.source.stream = str(content)
                    self.load_stream(self.source.stream)
            except Exception as ex:
                if not self.source.optional:
                    raise ex

    @abstractmethod
    def load_stream(self, stream):
        raise NotImplementedError

    def __str__(self):
        return f'{type(self).__name__} for {self._source.path} ({"Optional" if self._source.optional else "Required"})'
