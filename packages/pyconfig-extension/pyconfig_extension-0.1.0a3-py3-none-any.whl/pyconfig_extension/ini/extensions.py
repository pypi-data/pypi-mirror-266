from typing import Callable

from multipledispatch import dispatch

from pyconfig_extension import guard
from pyconfig_extension.abstracts.iconfiguration_builder import IConfigurationBuilder
from pyconfig_extension.abstracts.configuration_extensions import add
from pyconfig_extension.ini.ini_configuration_source import IniConfigurationSource
from pyconfig_extension.ini.ini_stream_configuration_source import IniStreamConfigurationSource


def add_ini_string(builder: IConfigurationBuilder, stream: str) -> IConfigurationBuilder:
    def config_function(x: IniStreamConfigurationSource):
        x.stream = stream

    return add(builder, IniStreamConfigurationSource, config_function)


@dispatch(IConfigurationBuilder, str)
def add_ini_file(builder: IConfigurationBuilder, path: str) -> IConfigurationBuilder:
    return add_ini_file(builder, path, True)


@dispatch(IConfigurationBuilder, object)
def add_ini_file(builder: IConfigurationBuilder, configure_source: Callable) -> IConfigurationBuilder:
    return add(builder, IniConfigurationSource, configure_source)


@dispatch(IConfigurationBuilder, str, bool)
def add_ini_file(builder: IConfigurationBuilder, path: str, optional: bool) -> IConfigurationBuilder:
    guard.check_none(path)

    def config_source(x: IniConfigurationSource):
        x.path = path
        x.optional = optional

    return add_ini_file(builder, config_source)
