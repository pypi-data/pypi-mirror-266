from pyconfig_extension.abstracts.iconfiguration_builder import IConfigurationSource, IConfigurationBuilder
from pyconfig_extension.abstracts.iconfiguration_provider import IConfigurationProvider


class EnvironmentVariablesConfigurationSource(IConfigurationSource):
    prefix: str | None

    def __init__(self, prefix: str | None = None):
        self.prefix = prefix

    def build(self, builder: IConfigurationBuilder) -> IConfigurationProvider:
        from pyconfig_extension.environment_variables.provider import EnvironmentVariablesConfigurationProvider
        return EnvironmentVariablesConfigurationProvider(self.prefix)
