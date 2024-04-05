from pyconfig_extension import guard
from pyconfig_extension.core.configuration_provider import ConfigurationProvider
from pyconfig_extension.core.ordinal_ignore_case_dict import OrdinalIgnoreCaseDict


def index_of(value: str, pattern: str):
    try:
        return value.index(pattern)
    except:
        return -1


class CommandLineConfigurationProvider(ConfigurationProvider):

    def __init__(self, args: list[str], switch_mappings: dict[str, str] = None):
        guard.check_none(args)
        super().__init__()
        self._args = args
        self._switch_mappings = switch_mappings
        if self._switch_mappings is not None:
            self._switch_mappings = self.__get_validated_switch_mappings(switch_mappings)

    @property
    def args(self) -> list[str]:
        return self._args

    def load(self):
        self._data = self.__load_args(self.args, self._switch_mappings)

    @staticmethod
    def __load_args(args, switch_mapping) -> OrdinalIgnoreCaseDict:
        result = OrdinalIgnoreCaseDict()
        args_iterator = iter(args)
        for current_arg in args_iterator:
            key_start_index = 0

            if current_arg.startswith("--"):
                key_start_index = 2
            elif current_arg.startswith("-"):
                key_start_index = 1
            elif current_arg.startswith("/"):
                current_arg = f"--{current_arg[1:]}"
                key_start_index = 2

            seperator = index_of(current_arg, "=")

            if seperator < 0:
                if key_start_index == 0:
                    continue
                if switch_mapping is not None and current_arg in switch_mapping:
                    key = switch_mapping[current_arg]
                # If the switch starts with a single "-" and it isn't in given mappings ,
                # it is an invalid usage so ignore it
                elif key_start_index == 1:
                    continue
                else:
                    key = current_arg[key_start_index:]

                try:
                    value = next(args_iterator)
                except StopIteration:
                    continue
            else:
                key_segment = current_arg[:seperator]

                if switch_mapping is not None and key_segment in switch_mapping:
                    key = switch_mapping[key_segment]
                # If the switch starts with a single "-" and it isn't in given mappings ,
                # it is an invalid usage so ignore it
                elif key_start_index == 1:
                    raise Exception(f"The short switch '{current_arg}' is not defined in the switch mappings.")
                else:
                    key = current_arg[key_start_index: seperator]
                value = current_arg[seperator + 1:]
            result[key] = value

        return result

    @staticmethod
    def __get_validated_switch_mappings(switch_mappings) -> OrdinalIgnoreCaseDict:
        result = OrdinalIgnoreCaseDict()
        for mapping_key in switch_mappings:
            mapping_key: str
            if not mapping_key.startswith("-") and not mapping_key.startswith("--"):
                raise Exception(
                    f"The switch mappings contain an invalid switch '{mapping_key}' , should start with '-' or '--'.")
            if mapping_key in result:
                raise Exception(
                    f"Keys in switch mappings are case-insensitive. A duplicated key '{mapping_key}' was found.")

            result[mapping_key] = switch_mappings[mapping_key]
        return result
