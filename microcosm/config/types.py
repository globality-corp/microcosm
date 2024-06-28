"""
Configuration types.

"""


def str_to_bool(val: str) -> bool:
    """Convert a string representation of truth to bool.

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True

    if val in ("n", "no", "f", "false", "off", "0"):
        return False

    raise ValueError("invalid truth value {!r}".format(val))


def boolean(value: bool | str) -> bool:
    """
    Configuration-friendly boolean type converter.

    Supports both boolean-valued and string-valued inputs (e.g. from env vars).

    """
    if isinstance(value, bool):
        return value

    if value == "":
        return False

    return str_to_bool(value)


def comma_separated_list(value: list[str] | str) -> list[str]:
    """
    Configuration-friendly list type converter.

    Supports both list-valued and string-valued inputs (which are comma-delimited lists of values, e.g. from env vars).

    """
    if isinstance(value, list):
        return value

    if value == "":
        return []

    return value.split(",")
