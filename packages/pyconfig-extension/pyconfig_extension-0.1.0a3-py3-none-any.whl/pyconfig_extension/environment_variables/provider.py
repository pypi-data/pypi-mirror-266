from pyconfig_extension.abstracts.configuration_path import KEY_DELIMITER
from pyconfig_extension.core.configuration_provider import ConfigurationProvider
from pyconfig_extension.core.ordinal_ignore_case_dict import OrdinalIgnoreCaseDict

MY_SQL_SERVER_PREFIX = "MYSQLCONNSTR_"
SQL_AZURE_SERVER_PREFIX = "SQLAZURECONNSTR_"
SQL_SERVER_PREFIX = "SQLCONNSTR_"
CUSTOM_CONNECTION_STRING_PREFIX = "CUSTOMCONNSTR_"


class EnvironmentVariablesConfigurationProvider(ConfigurationProvider):
    def __init__(self, prefix: str | None = None):
        super().__init__()
        self.__prefix = "" if prefix is None else prefix
        self.__normal_prefix = self.__normalize(self.__prefix)

    def load_data(self, data: dict[str, str]):
        res = OrdinalIgnoreCaseDict()
        for key in data:
            value = data[key]
            self.__add_if_normalized_key_matches_prefix(res, self.__normalize(key), value)
        self._data = res

    def __add_if_normalized_key_matches_prefix(self, data: OrdinalIgnoreCaseDict, normalized_key: str, value: str):
        if normalized_key.lower().startswith(self.__normal_prefix.lower()):
            data[normalized_key[len(self.__normal_prefix):]] = value

    @staticmethod
    def __normalize(key: str):
        return key.replace("__", KEY_DELIMITER)

    def __str__(self):
        return f"{type(self).__name__} Prefix: '{self.__prefix}'"
