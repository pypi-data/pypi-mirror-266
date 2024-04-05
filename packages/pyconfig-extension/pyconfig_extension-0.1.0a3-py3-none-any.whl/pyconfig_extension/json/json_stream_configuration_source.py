from pyconfig_extension.abstracts.iconfiguration_builder import IConfigurationBuilder
from pyconfig_extension.abstracts.iconfiguration_provider import IConfigurationProvider
from pyconfig_extension.abstracts.stream_configuration_source import StreamConfigurationSource


class JsonStreamConfigurationSource(StreamConfigurationSource):
    def build(self, builder: IConfigurationBuilder) -> IConfigurationProvider:
        from pyconfig_extension.json.json_stream_configuration_provider import JsonStreamConfigurationProvider
        return JsonStreamConfigurationProvider(self)
