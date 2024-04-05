from abc import ABC, abstractmethod

from pyconfig_extension.abstracts.iconfiguration_provider import IConfigurationProvider
from pyconfig_extension.abstracts.iconfiguration_root import IConfigurationRoot


class IConfigurationBuilder(ABC):

    @property
    @abstractmethod
    def properties(self) -> dict[str, object]:
        raise NotImplementedError

    @property
    @abstractmethod
    def sources(self) -> list['IConfigurationSource']:
        raise NotImplementedError

    @abstractmethod
    def add(self, source: 'IConfigurationSource') -> 'IConfigurationBuilder':
        raise NotImplementedError

    @abstractmethod
    def build(self) -> IConfigurationRoot:
        raise NotImplementedError


class IConfigurationSource(ABC):

    @abstractmethod
    def build(self, builder: IConfigurationBuilder) -> IConfigurationProvider:
        raise NotImplementedError
