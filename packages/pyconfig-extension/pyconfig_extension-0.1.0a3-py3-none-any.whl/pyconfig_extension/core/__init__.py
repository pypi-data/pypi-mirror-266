from pyconfig_extension.abstracts.iconfiguration_builder import IConfigurationBuilder
from pyconfig_extension.core.extensions import add_configuration

IConfigurationBuilder.add_configuration = add_configuration
