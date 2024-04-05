from pyconfig_extension.abstracts.iconfiguration_builder import IConfigurationBuilder
from pyconfig_extension.environment_variables.source import EnvironmentVariablesConfigurationSource


def add_environment_variables(builder: IConfigurationBuilder, prefix: str | None = None) -> IConfigurationBuilder:
    builder.add(EnvironmentVariablesConfigurationSource(prefix))
    return builder
