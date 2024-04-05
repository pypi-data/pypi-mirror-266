
from pyconfig_extension.file.file_configuration_provider import FileConfigurationProvider
from pyconfig_extension.file.file_configuration_source import FileConfigurationSource
from pyconfig_extension.json.json_configuration_file_parser import JsonConfigurationFileParser


class JsonConfigurationProvider(FileConfigurationProvider):

    def __init__(self, source: FileConfigurationSource):
        super().__init__(source)

    def load_stream(self, stream):
        self._data = JsonConfigurationFileParser.parse(stream)
