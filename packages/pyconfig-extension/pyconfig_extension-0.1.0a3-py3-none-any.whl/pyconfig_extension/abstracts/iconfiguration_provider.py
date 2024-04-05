from abc import ABC, abstractmethod


class IConfigurationProvider(ABC):
    """
    Provides configuration key/values for an application.
    """

    @abstractmethod
    def try_get(self, key: str) -> tuple[bool, str | None]:
        raise NotImplementedError

    @abstractmethod
    def set(self, key: str, value: str):
        """
        Sets a configuration value for the specified key.
        :param key: The key.
        :param value: The value.
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def load(self):
        """
        Loads configuration values from the source represented by this 'IConfigurationProvider'
        """
        raise NotImplementedError

    @abstractmethod
    def get_child_keys(self, earlier_keys: list[str], parent_path: str | None) -> list[str]:
        """
        Returns the immediate descendant configuration keys for a given parent path based on this
        'IConfigurationProvider's data and the set of keys returned by all the preceding
        :param earlier_keys: The child keys returned by the preceding providers for the same parent path.
        :param parent_path: The parent path.
        :return: The child keys.
        """
        raise NotImplementedError

    def get(self, key: str):
        checked, value = self.try_get(key)
        if checked:
            return value
        raise Exception(f"key not found key={key}")
