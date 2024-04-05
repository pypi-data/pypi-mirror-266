from multipledispatch import dispatch

from pyconfig_extension.abstracts.iconfiguration_builder import IConfigurationBuilder
from pyconfig_extension.command_line.source import CommandLineConfigurationSource


@dispatch(IConfigurationBuilder, list)
def add_command_line(builder: IConfigurationBuilder, args: list[str]) -> IConfigurationBuilder:
    return add_command_line(builder, args, None)


@dispatch(IConfigurationBuilder, list, dict)
def add_command_line(builder: IConfigurationBuilder, args: list[str],
                     switch_mappings: dict[str, str] | None) -> IConfigurationBuilder:
    source = CommandLineConfigurationSource(args, switch_mappings)
    return builder.add(source)
