from io import StringIO

from pyconfig_extension.abstracts.configuration_path import KEY_DELIMITER
from pyconfig_extension.abstracts.stream_configuration_provider import StreamConfigurationProvider
from pyconfig_extension.core.ordinal_ignore_case_dict import OrdinalIgnoreCaseDict
from pyconfig_extension.ini.ini_stream_configuration_source import IniStreamConfigurationSource
import os


def get_index(inp: str, delim: str) -> int:
    try:
        return inp.index(delim)
    except:
        return -1


class IniStreamConfigurationProvider(StreamConfigurationProvider):

    def __init__(self, source: IniStreamConfigurationSource):
        super().__init__(source)

    def load_stream(self, stream):
        self._data = self.read(stream)

    @staticmethod
    def read(stream: str) -> OrdinalIgnoreCaseDict:
        result = OrdinalIgnoreCaseDict()
        section_prefix = ""
        lines = stream.splitlines()
        for line in lines:
            raw_line = line.strip()
            # ignore blank lines
            if len(raw_line) == 0:
                continue
            # ignore comments
            if raw_line[0] in ';#/':
                continue
            # [Section:header]
            if raw_line[0] == '[' and raw_line[-1] == ']':
                # remove the brackets
                section_prefix = raw_line[1:-1].strip() + KEY_DELIMITER
                continue

            # key = value or "value"
            seperator = get_index(raw_line, "=")
            if seperator < 0:
                raise Exception(f"Unrecognized line format: '{line}'.")
            key = section_prefix + raw_line[: seperator].strip()
            value = raw_line[seperator + 1:].strip()
            if len(value) > 0 and value[0] == '"' and value[-1] == '"':
                value = value[1:-1]

            if key in result:
                raise Exception(f"A duplicate key '{key}' was found.")
            result[key] = value
        return result
