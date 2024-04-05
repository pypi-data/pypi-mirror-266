from pyconfig_extension import guard

KEY_DELIMITER: str = ":"


def combine(*path_segments: str):
    guard.check_none(path_segments)
    res = ':'.join(path_segments)
    return res


def get_section_key(path: str | None):
    if path is None or len(path) == 0:
        return path

    try:
        index = path.rindex(KEY_DELIMITER)
        return path[index + 1:]
    except ValueError:
        return path


def get_parent_path(path: str | None):
    if path is None or len(path) == 0:
        return None

    try:
        index = path.rindex(KEY_DELIMITER)
        return path[:index]
    except ValueError:
        return None
