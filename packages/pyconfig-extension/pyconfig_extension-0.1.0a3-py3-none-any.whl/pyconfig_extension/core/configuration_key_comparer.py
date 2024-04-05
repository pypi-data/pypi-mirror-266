import math

KEY_DELIMITER = ":"


def __skip_ahead_on_delimiter(inp: str):
    for i in range(len(inp)):
        if inp[i] != KEY_DELIMITER:
            return inp[i:]
    return ""


def is_integer(s: str) -> bool:
    """
    Checks if a string represents an integer value.

    Returns True if the string is an integer, False otherwise.
    """
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


def __just_compare(a: str | None, b: str | None) -> int:
    a_is_int = is_integer(a)
    b_is_int = is_integer(b)

    if not a_is_int and not b_is_int:
        if a.lower() < b.lower():
            return -1
        elif a.lower() > b.lower():
            return 1
        return 0
    elif a_is_int and b_is_int:
        a = int(a)
        b = int(b)
        if a < b:
            return -1
        elif a > b:
            return 1
        else:
            return 0
    else:

        if a_is_int:
            return -1
        return 1


def __delimiter_index(val: str):
    try:
        return val.index(KEY_DELIMITER)
    except:
        return -1


def compare(x: str | None, y: str | None) -> int:
    x = "" if x is None else x
    y = "" if y is None else y
    x = __skip_ahead_on_delimiter(x)
    y = __skip_ahead_on_delimiter(y)

    while len(x) != 0 and len(y) != 0:
        x_delimiter_index = __delimiter_index(x)
        y_delimiter_index = __delimiter_index(y)

        a = x if x_delimiter_index == -1 else x[0:x_delimiter_index]
        b = y if y_delimiter_index == -1 else y[0:y_delimiter_index]
        compare_result = __just_compare(a, b)

        if compare_result != 0:
            return compare_result

        x = "" if x_delimiter_index == -1 else __skip_ahead_on_delimiter(x[x_delimiter_index + 1:])
        y = "" if y_delimiter_index == -1 else __skip_ahead_on_delimiter(y[y_delimiter_index + 1:])

    if len(x) == 0:
        if len(y) == 0:
            return 0
        return -1
    return 1
