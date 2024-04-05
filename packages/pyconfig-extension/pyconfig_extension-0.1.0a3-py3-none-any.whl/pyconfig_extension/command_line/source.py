from pyconfig_extension.abstracts.iconfiguration_builder import IConfigurationSource, IConfigurationBuilder
from pyconfig_extension.abstracts.iconfiguration_provider import IConfigurationProvider


class CommandLineConfigurationSource(IConfigurationSource):
    switch_mappings: dict[str, str]
    args: list[str] = []

    def __init__(self, args: list[str] = None, switch_mappings: dict[str, str] = None):
        self.args = args if args is not None else []
        self.switch_mappings = switch_mappings

    def build(self, builder: IConfigurationBuilder) -> IConfigurationProvider:
        from pyconfig_extension.command_line.provider import CommandLineConfigurationProvider
        return CommandLineConfigurationProvider(self.args, self.switch_mappings)
