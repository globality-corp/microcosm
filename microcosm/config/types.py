"""
Configuration types.

"""
from distutils.util import strtobool


def boolean(value):
    """
    Configuration-friendly boolean type converter.

    Supports both boolean-valued and string-valued inputs (e.g. from env vars).

    """
    if isinstance(value, bool):
        return value

    if value == "":
        return False

    return strtobool(value)


def integer(value):
    """
    Configuration-friendly integer type converter.

    Supports both integer-valued and string-valued inputs (e.g. from env vars).

    """
    if isinstance(value, int):
        return value

    return int(value)
