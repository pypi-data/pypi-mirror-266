from pyconfig_extension.abstracts.iconfiguration_builder import IConfigurationBuilder
from pyconfig_extension.abstracts.iconfiguration_provider import IConfigurationProvider
from pyconfig_extension.file.file_configuration_source import FileConfigurationSource


class JsonConfigurationSource(FileConfigurationSource):
    def __init__(self, stream=None, path: str = None, optional: bool = False):
        super().__init__(stream, path, optional)

    def build(self, builder: IConfigurationBuilder) -> IConfigurationProvider:
        self.ensure_defaults(builder)
        from pyconfig_extension.json.json_configuration_provider import JsonConfigurationProvider
        return JsonConfigurationProvider(self)
