from typing import Callable

from multipledispatch import dispatcher, dispatch


class BindingPoint:

    def __init__(self, initial_value=None, is_readonly: bool = False):
        self.__is_readonly = is_readonly
        self.__initial_value = None
        self._initial_value_provider = None
        if isinstance(initial_value, Callable):
            self._initial_value_provider = initial_value
        else:
            self.__initial_value = initial_value
        self._is_value_set = False
        self._set_value = None

    @property
    def is_readonly(self) -> bool:
        return self.__is_readonly

    @property
    def has_new_value(self):
        if self.is_readonly:
            return False
        return self._is_value_set

    @property
    def value(self):
        if self._is_value_set:
            return self._set_value
        else:
            if self.__initial_value is not None:
                return self.__initial_value
            elif self._initial_value_provider is not None:
                return self._initial_value_provider()
            return None

    def set_value(self, new_value):
        assert not self.is_readonly
        assert not self._is_value_set
        self._is_value_set = True
        self._set_value = new_value

    def try_set_value(self, new_value):
        if not self.is_readonly:
            self.set_value(new_value)
