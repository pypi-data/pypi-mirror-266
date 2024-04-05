from pyconfig_extension.abstracts.iconfiguration_builder import IConfigurationBuilder
from pyconfig_extension.abstracts.iconfiguration_provider import IConfigurationProvider
from pyconfig_extension.file.file_configuration_source import FileConfigurationSource


class IniConfigurationSource(FileConfigurationSource):

    def build(self, builder: IConfigurationBuilder) -> IConfigurationProvider:
        from pyconfig_extension.ini.ini_configuration_provider import IniConfigurationProvider
        return IniConfigurationProvider(self)
