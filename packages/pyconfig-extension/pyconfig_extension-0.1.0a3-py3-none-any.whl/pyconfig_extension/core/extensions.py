from multipledispatch import dispatch

from pyconfig_extension import guard
from pyconfig_extension.abstracts.iconfiguration import IConfiguration
from pyconfig_extension.abstracts.iconfiguration_builder import IConfigurationBuilder
from pyconfig_extension.core.chained_configuration_source import ChainedConfigurationSource
from pyconfig_extension.core.memory_configuration_source import MemoryConfigurationSource


def add_configuration(configuration_builder: IConfigurationBuilder, config: IConfiguration,
                      should_dispose_configuration: bool = False):
    guard.check_none(configuration_builder)
    guard.check_none(config)

    source = ChainedConfigurationSource(config, should_dispose_configuration)
    configuration_builder.add(source)
    return configuration_builder


@dispatch(IConfigurationBuilder)
def add_in_memory_collection(builder: IConfigurationBuilder) -> IConfigurationBuilder:
    builder.add(MemoryConfigurationSource())
    return builder


@dispatch(IConfigurationBuilder, dict)
def add_in_memory_collection(builder: IConfigurationBuilder, internal_data: dict[str, str]) -> IConfigurationBuilder:
    builder.add(MemoryConfigurationSource(internal_data))
    return builder
