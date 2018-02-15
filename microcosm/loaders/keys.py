"""
Key expansion.

"""


def expand_config(dct,
                  separator='.',
                  skip_to=0,
                  key_func=lambda key: key.lower(),
                  key_parts_filter=lambda key_parts: True,
                  value_func=lambda value: value):
    """
    Expand a dictionary recursively by splitting keys along the separator.

    :param dct: a non-recursive dictionary
    :param separator: a separator charactor for splitting dictionary keys
    :param skip_to: index to start splitting keys on; can be used to skip over a key prefix
    :param key_func: a key mapping function
    :param key_parts_filter: a filter function for excluding keys
    :param value_func: a value mapping func

    """
    config = {}

    for key, value in dct.items():
        key_separator = separator(key) if callable(separator) else separator
        key_parts = key.split(key_separator)
        if not key_parts_filter(key_parts):
            continue
        key_config = config
        # skip prefix
        for key_part in key_parts[skip_to:-1]:
            key_config = key_config.setdefault(key_func(key_part), dict())
        key_config[key_func(key_parts[-1])] = value_func(value)

    return config
