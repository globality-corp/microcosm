"""
Configuration types.

"""
from typing import List, Union


def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif val in ("n", "no", "f", "false", "off", "0"):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))


def boolean(value: Union[bool, str]) -> bool:
    """
    Configuration-friendly boolean type converter.

    Supports both boolean-valued and string-valued inputs (e.g. from env vars).

    """
    if isinstance(value, bool):
        return value

    if value == "":
        return False

    return bool(strtobool(value))


def comma_separated_list(value: Union[List[str], str]) -> List[str]:
    """
    Configuration-friendly list type converter.

    Supports both list-valued and string-valued inputs (which are comma-delimited lists of values, e.g. from env vars).

    """
    if isinstance(value, list):
        return value

    if value == "":
        return []

    return value.split(",")
