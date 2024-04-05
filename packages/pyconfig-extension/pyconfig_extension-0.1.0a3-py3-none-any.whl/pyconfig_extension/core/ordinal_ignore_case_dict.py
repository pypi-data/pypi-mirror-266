class OrdinalIgnoreCaseDict:
    def __init__(self):
        self.__data = {}
        self.__low_key_data: dict[str, str] = {}

    def __setitem__(self, key: str, value):
        if not isinstance(key, str):
            ValueError("key should be string")
        dict_key = self.__dict_key(key)
        if dict_key not in self.__data:
            self.__data[dict_key] = value
            self.__low_key_data[key.lower()] = key
        else:
            del self.__data[dict_key]
            self.__data[key] = value
            self.__low_key_data[key.lower()] = key

    def __getitem__(self, key: str):
        if not isinstance(key, str):
            ValueError("key should be string")
        dict_key = self.__dict_key(key)
        return self.__data[dict_key]

    def __delitem__(self, key: str):
        if not isinstance(key, str):
            ValueError("key should be string")
        dict_key = self.__dict_key(key)
        self.__data.__delitem__(dict_key)
        self.__low_key_data.__delitem__(key.lower())

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return iter(self.__data)

    def __contains__(self, key: str):
        if not isinstance(key, str):
            ValueError("key should be string")
        dict_key = self.__dict_key(key)
        return self.__data.__contains__(dict_key)

    def try_get(self, key: str) -> tuple[bool, object | None]:
        dict_key = self.__dict_key(key)
        if dict_key in self.__data:
            return True, self.__data[dict_key]
        return False, None

    def __dict_key(self, key: str):
        dict_key = key
        if key.lower() in self.__low_key_data:
            dict_key = self.__low_key_data[key.lower()]
        return dict_key
