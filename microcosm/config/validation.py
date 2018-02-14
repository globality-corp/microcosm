"""
Validation for configuration.

"""
from microcosm.config.model import Requirement


def required(*args, **kwargs):
    """
    Fluent requirement declaration.

    """
    return Requirement(*args, **kwargs)


def typed(*args, **kwargs):
    """
    Fluent requirement declaration.

    """
    return Requirement(*args, required=False, **kwargs)


def validate(defaults, metadata, config):
    """
    Validate configuration.

    """
    for path, _, default, parent, value in zip_dicts(defaults, config):
        if isinstance(default, Requirement):
            # validate the current value and assign the output
            parent[path[-1]] = default.validate(metadata, path, value)


def zip_dicts(left, right, prefix=()):
    """
    Modified zip through two dictionaries.

    Iterate through all keys of left dictionary, returning:

      -  A nested path
      -  A value and parent for both dictionaries

    """
    for key, left_value in left.items():
        path = prefix + (key, )
        right_value = right.get(key)

        if isinstance(left_value, dict):
            yield from zip_dicts(left_value, right_value or {}, path)
        else:
            yield path, left, left_value, right, right_value
