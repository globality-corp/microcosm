"""
Configuration types.

"""
from distutils.util import strtobool
from typing import List, Union


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
