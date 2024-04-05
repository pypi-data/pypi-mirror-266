from abc import ABC

from pyconfig_extension.abstracts.iconfiguration_builder import IConfigurationSource


class StreamConfigurationSource(IConfigurationSource, ABC):
    stream: object
    """
    The stream containing the configuration data.
    """
