from multipledispatch import dispatch

from pyconfig_extension.abstracts.iconfiguration_builder import IConfigurationBuilder
import pyconfig_extension.abstracts.configuration_extensions as config_ext
from pyconfig_extension.json.json_configuration_source import JsonConfigurationSource
from pyconfig_extension.json.json_stream_configuration_source import JsonStreamConfigurationSource


def add_json_string(builder: IConfigurationBuilder, stream):
    def configure(x: IConfigurationBuilder):
        x.stream = stream

    return config_ext.add(builder, JsonStreamConfigurationSource, configure)


@dispatch(IConfigurationBuilder, str)
def add_json_file(builder: IConfigurationBuilder, path: str):
    return add_json_file(builder, path, False)


@dispatch(IConfigurationBuilder, str, bool)
def add_json_file(builder: IConfigurationBuilder, path: str, optional: bool):
    def configure(x: JsonConfigurationSource):
        x.optional = optional
        x.path = path

    return config_ext.add(builder, JsonConfigurationSource, configure)
