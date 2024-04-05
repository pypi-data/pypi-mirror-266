from pyconfig_extension.abstracts.stream_configuration_provider import StreamConfigurationProvider
from pyconfig_extension.json.json_stream_configuration_source import JsonStreamConfigurationSource
from pyconfig_extension.json.json_configuration_file_parser import JsonConfigurationFileParser


class JsonStreamConfigurationProvider(StreamConfigurationProvider):

    def __init__(self, source: JsonStreamConfigurationSource):
        super().__init__(source)

    def load_stream(self, stream):
        self._data = JsonConfigurationFileParser.parse(stream)
