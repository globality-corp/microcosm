"""
Validation for configuration.

"""
from typing import Any

from microcosm.config.model import Configuration, Requirement
from microcosm.metadata import Metadata


def required(*args, **kwargs) -> Requirement:
    """
    Fluent requirement declaration.

    """
    return Requirement(*args, **kwargs)


def typed(*args, **kwargs) -> Requirement:
    """
    Fluent requirement declaration.

    """
    kwargs["required"] = False
    return Requirement(*args, **kwargs)


def validate(defaults, metadata: Metadata, config: Configuration) -> None:
    """
    Validate configuration.

    """
    for path, _, default, parent, value in zip_dicts(defaults, config):
        if isinstance(default, Requirement):
            # validate the current value and assign the output
            parent[path[-1]] = default.validate(metadata, path, value)


def zip_dicts(left: dict[Any, Any], right: dict[Any, Any], prefix: tuple[str, ...] = ()):
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
