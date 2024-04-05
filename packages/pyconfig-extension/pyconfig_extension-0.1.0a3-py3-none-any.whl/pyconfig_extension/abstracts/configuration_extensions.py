from typing import Generator, Callable

from pyconfig_extension.abstracts.iconfiguration import IConfiguration ,IConfigurationSection
from pyconfig_extension.abstracts.iconfiguration_builder import IConfigurationBuilder


def as_generator(self: IConfiguration, make_paths_relative: bool = False) -> Generator[tuple[str, str], None, None]:
    stack: list[IConfiguration] = [self]

    prefix_length = 0
    if make_paths_relative and isinstance(self, IConfigurationSection):
        prefix_length = len(self.path) + 1

    while len(stack) > 0:
        config: IConfiguration = stack.pop()

        if isinstance(config, IConfigurationSection) and (not make_paths_relative or config != self):
            yield config.path[prefix_length:], config.value

        for child in config.get_children():
            stack.append(child)


def add(builder: IConfigurationBuilder, config_type: type,
        configure_source: Callable = None) -> IConfigurationBuilder:
    source = config_type()
    if configure_source is not None:
        configure_source(source)
    return builder.add(source)
