"""
Configuration types.

"""
from distutils.util import strtobool
from re import compile as re_compile
from json import loads
from json.decoder import JSONDecodeError


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


def string_list(value):
    if isinstance(value, list):
        return value

    pattern = re_compile("\['(.*)'\]")
    match = pattern.match(value)

    if not match:
        return []

    try:
        return loads(value.replace("'", "\""))
    except JSONDecodeError:
        return []


def int_list(value):
    if isinstance(value, list):
        return [int(item) for item in value]

    pattern = re_compile("\['(.*)'\]")
    match = pattern.match(value)

    if not match:
        return []

    try:
        parsed_int_list = loads(value.replace("'", "\""))
        return [int(item) for item in parsed_int_list]
    except JSONDecodeError:
        return []
