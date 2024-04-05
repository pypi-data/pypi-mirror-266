from abc import ABC

from pyconfig_extension.abstracts.iconfiguration_builder import IConfigurationSource, IConfigurationBuilder
from pyconfig_extension.abstracts.iconfiguration_provider import IConfigurationProvider


class FileConfigurationSource(IConfigurationSource, ABC):
    path: str
    """
    The path to the file.
    """
    # file_provider: object
    # """
    # Used to access the contents of the file.
    # """
    optional: bool
    """
    Determines if loading the file is optional.
    """

    def __init__(self, stream=None, path: str = None, optional: bool = False):
        self.stream = stream
        self.path: str = path
        self.optional = optional

    def ensure_defaults(self, builder: IConfigurationBuilder):
        pass
