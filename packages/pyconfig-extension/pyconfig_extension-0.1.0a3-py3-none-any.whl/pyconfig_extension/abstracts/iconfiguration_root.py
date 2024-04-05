from abc import ABC, abstractmethod

from pyconfig_extension.abstracts.iconfiguration_provider import IConfigurationProvider
from pyconfig_extension.abstracts.iconfiguration import IConfiguration


class IConfigurationRoot(IConfiguration, ABC):

    @abstractmethod
    def reload(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def providers(self) -> list[IConfigurationProvider]:
        raise NotImplementedError
