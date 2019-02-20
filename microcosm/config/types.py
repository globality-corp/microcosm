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


def comma_separated_list(value):
    """
    Configuration-friendly list type converter.

    Supports both list-valued and string-valued inputs (which are comma-delimited lists of values, e.g. from env vars).

    """
    if isinstance(value, list):
        return value

    if value == "":
        return []

    return value.split(",")
