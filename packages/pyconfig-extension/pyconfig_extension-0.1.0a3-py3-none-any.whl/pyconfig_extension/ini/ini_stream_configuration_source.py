from pyconfig_extension.abstracts.iconfiguration_builder import IConfigurationBuilder
from pyconfig_extension.abstracts.iconfiguration_provider import IConfigurationProvider
from pyconfig_extension.abstracts.stream_configuration_source import StreamConfigurationSource


class IniStreamConfigurationSource(StreamConfigurationSource):
    def build(self, builder: IConfigurationBuilder) -> IConfigurationProvider:
        from pyconfig_extension.ini.ini_stream_configuration_provider import IniStreamConfigurationProvider
        return IniStreamConfigurationProvider(self)
