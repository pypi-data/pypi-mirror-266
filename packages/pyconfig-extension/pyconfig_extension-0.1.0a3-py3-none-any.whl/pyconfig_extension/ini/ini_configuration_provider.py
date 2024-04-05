from pyconfig_extension.file.file_configuration_provider import FileConfigurationProvider
from pyconfig_extension.ini.ini_configuration_source import IniConfigurationSource
from pyconfig_extension.ini.ini_stream_configuration_provider import IniStreamConfigurationProvider


class IniConfigurationProvider(FileConfigurationProvider):
    def __init__(self, source: IniConfigurationSource):
        super().__init__(source)

    def load_stream(self, stream):
        self._data = IniStreamConfigurationProvider.read(stream)
