from abc import ABC

from multipledispatch import dispatch

from pyconfig_extension.abstracts.iconfiguration_provider import IConfigurationProvider
from pyconfig_extension.core.ordinal_ignore_case_dict import OrdinalIgnoreCaseDict
import pyconfig_extension.abstracts.configuration_path as conf_path


class ConfigurationProvider(IConfigurationProvider, ABC):
    def __init__(self):
        self._data = OrdinalIgnoreCaseDict()

    def try_get(self, key: str) -> tuple[bool, str | None]:
        return self._data.try_get(key)

    def set(self, key: str, value: str):
        self._data[key] = value

    def load(self):
        pass

    def get_child_keys(self, earlier_keys: list[str], parent_path: str | None):
        results: list[str] = []

        if parent_path is None:
            for key in self._data:
                results.append(self.__segment(key, 0))
        else:
            assert conf_path.KEY_DELIMITER == ":"
            for key in self._data:
                if len(key) > len(parent_path) and \
                        key.lower().startswith(parent_path.lower()) and \
                        key[len(parent_path)] == conf_path.KEY_DELIMITER:
                    results.append(self.__segment(key, len(parent_path) + 1))

        results.extend(earlier_keys)
        results.sort()
        return results

    @staticmethod
    def __segment(key: str, prefix_length) -> str:
        try:
            index = key.index(conf_path.KEY_DELIMITER, prefix_length)
            return key[prefix_length: index]
        except ValueError:
            return key[prefix_length:]

    def __str__(self):
        return type(self).__name__
