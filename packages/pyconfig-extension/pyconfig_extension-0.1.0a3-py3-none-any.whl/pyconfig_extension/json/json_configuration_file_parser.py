from pyconfig_extension.abstracts.configuration_path import KEY_DELIMITER
from pyconfig_extension.core.ordinal_ignore_case_dict import OrdinalIgnoreCaseDict
import json5


class JsonConfigurationFileParser:

    def __init__(self):
        self._path: list[str] = []
        self._data = OrdinalIgnoreCaseDict()

    @staticmethod
    def parse(stream) -> OrdinalIgnoreCaseDict:
        parser = JsonConfigurationFileParser()
        return parser.parse_stream(stream)

    def parse_stream(self, stream) -> OrdinalIgnoreCaseDict:
        root = json5.loads(stream)
        self.__visit_object_element(root)
        return self._data

    def __visit_object_element(self, element):
        is_empty = True
        for key in element:
            is_empty = False
            self.__enter_context(key)
            self.__visit_value(element[key])
            self.__exit_context()
        self.__set_null_if_element_is_empty(is_empty)

    def __set_null_if_element_is_empty(self, is_empty: bool):
        if is_empty and len(self._path) > 0:
            key = self._path[-1]
            self._data[key] = None

    def __visit_value(self, value):
        if isinstance(value, str) or \
                isinstance(value, bool) or \
                isinstance(value, int) or \
                isinstance(value, float):
            key = self._path[-1]
            if key in self._data:
                raise ValueError(f"A duplicate key '{key}' was found.")
            self._data[key] = str(value)
        elif value is None:
            key = self._path[-1]
            self._data[key] = ""
        elif isinstance(value, dict):
            self.__visit_object_element(value)
        elif isinstance(value, list):
            self.__visit_array_elements(value)
        else:
            raise ValueError(f"Unsupported JSON token '{type(value)}' was found.")

    def __visit_array_elements(self, value: list):
        index = 0
        for element in value:
            self.__enter_context(str(index))
            self.__visit_value(element)
            self.__exit_context()
            index += 1

        self.__set_null_if_element_is_empty(is_empty=index == 0)

    def __enter_context(self, context: str):
        path = self._path[-1] + KEY_DELIMITER + context if len(self._path) > 0 else context
        self._path.append(path)

    def __exit_context(self):
        self._path.pop()
