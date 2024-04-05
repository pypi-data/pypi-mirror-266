from multipledispatch import dispatch

from pyconfig_extension import guard
from pyconfig_extension.abstracts.iconfiguration import IConfigurationSection
from pyconfig_extension.abstracts.iconfiguration_root import IConfigurationRoot
import pyconfig_extension.abstracts.configuration_path as path_conf
import pyconfig_extension.core._internal_configuration_root_extensions as root_ext


class ConfigurationSection(IConfigurationSection):

    def __init__(self, root: IConfigurationRoot, path: str):
        guard.check_none(root)
        guard.check_none(path)

        self.__root = root
        self.__path = path
        self.__key = None

    @property
    def key(self) -> str:
        if self.__key is None:
            self.__key = path_conf.get_section_key(self.__path)
        return self.__key

    @property
    def path(self) -> str:
        return self.__path

    @property
    def value(self) -> str | None:
        return self.__root[self.path]

    @value.setter
    def value(self, val: str):
        self.__root[self.path] = val

    @dispatch(str)
    def __getitem__(self, key: str) -> str | None:
        root_key = path_conf.combine(self.path, key)
        return self.__root[root_key]

    def __setitem__(self, key: str, value: str | None):
        root_key = path_conf.combine(self.path, key)
        self.__root[root_key] = value

    def get_section(self, key: str) -> IConfigurationSection:
        root_key = path_conf.combine(self.path, key)
        return self.__root.get_section(root_key)

    def get_children(self) -> list[IConfigurationSection]:
        return root_ext.get_children_implementation(self.__root, self.path)

    def __str__(self):
        return f"path ={self.path} ,key ={self.key} , value= {self.value}"


