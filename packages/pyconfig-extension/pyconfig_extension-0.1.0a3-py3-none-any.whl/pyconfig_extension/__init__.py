from pyconfig_extension.abstracts.iconfiguration import IConfiguration, IConfigurationSection
from pyconfig_extension.abstracts.iconfiguration_provider import IConfigurationProvider
from pyconfig_extension.abstracts.iconfiguration_builder import IConfigurationBuilder
from pyconfig_extension.core.configuration_builder import ConfigurationBuilder

import pyconfig_extension.core.extensions as core_extension
import pyconfig_extension.abstracts.configuration_extensions as abstract_extension
import pyconfig_extension.json.extensions as json_extension
import pyconfig_extension.ini.extensions as ini_extension
import pyconfig_extension.command_line.extensions as cmd_extension
import pyconfig_extension.environment_variables.extensions as env_extension


def add_json_file(*args):
    return json_extension.add_json_file(*args)


def add_json_string(*args):
    return json_extension.add_json_string(*args)


def add_ini_file(*args):
    return ini_extension.add_ini_file(*args)


def add_ini_string(*args):
    return ini_extension.add_ini_string(*args)


def add_command_line(*args):
    return cmd_extension.add_command_line(*args)


def add_in_memory_collection(*args):
    return core_extension.add_in_memory_collection(*args)


def add_configuration(*args):
    return core_extension.add_configuration(*args)


IConfigurationBuilder.add_configuration = add_configuration
IConfigurationBuilder.add_in_memory_collection = add_in_memory_collection

IConfigurationBuilder.add_ini_file = add_ini_file
IConfigurationBuilder.add_ini_string = add_ini_string

IConfigurationBuilder.add_json_file = add_json_file
IConfigurationBuilder.add_json_string = add_json_string

IConfigurationBuilder.add_command_line = add_command_line
