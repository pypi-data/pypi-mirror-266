from pyconfig_extension.abstracts.iconfiguration import IConfiguration
from pyconfig_extension.abstracts.iconfiguration_builder import IConfigurationSource, IConfigurationBuilder
from pyconfig_extension.abstracts.iconfiguration_provider import IConfigurationProvider


class ChainedConfigurationSource(IConfigurationSource):

    def __init__(self, configuration: IConfiguration, should_exit_configuration: bool = False):
        self._configuration = configuration
        self._should_exit_configuration = should_exit_configuration

    @property
    def configuration(self) -> IConfiguration:
        return self._configuration

    @configuration.setter
    def configuration(self, value: IConfiguration):
        self._configuration = value

    @property
    def should_exit_configuration(self) -> bool:
        return self._should_exit_configuration

    @should_exit_configuration.setter
    def should_exit_configuration(self, value: bool):
        self._should_exit_configuration = value

    def build(self, builder: IConfigurationBuilder) -> IConfigurationProvider:
        from pyconfig_extension.core.chained_configuration_provider import ChainedConfigurationProvider
        return ChainedConfigurationProvider(self)
