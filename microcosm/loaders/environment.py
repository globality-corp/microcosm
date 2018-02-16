"""
Enviroment-variable based loaders.

Uses a naming convention to map environment variables to nested configuration.

"""
from json import loads
from os import environ

from microcosm.loaders.keys import expand_config


def _load_from_environ(metadata, value_func=None):
    """
    Load configuration from environment variables.

    Any environment variable prefixed with the metadata's name will be
    used to recursively set dictionary keys, splitting on '__'.

    :param value_func: a mutator for the envvar's value (if any)

    """
    # We'll match the ennvar name against the metadata's name. The ennvar
    # name must be uppercase and hyphens in names converted to underscores.
    #
    # | envar       | name    | matches? |
    # +-------------+---------+----------+
    # | FOO_BAR     | foo     | yes      |
    # | FOO_BAR     | bar     | no       |
    # | foo_bar     | bar     | no       |
    # | FOO_BAR_BAZ | foo_bar | yes      |
    # | FOO_BAR_BAZ | foo-bar | yes      |
    # +-------------+---------+----------+

    prefix = metadata.name.upper().replace("-", "_")

    return expand_config(
        environ,
        separator="__",
        skip_to=1,
        key_parts_filter=lambda key_parts: len(key_parts) > 1 and key_parts[0] == prefix,
        value_func=lambda value: value_func(value) if value_func else value,
    )


def load_from_environ(metadata):
    """
    Load configuration from environment variables.

    """
    return _load_from_environ(metadata)


def load_from_environ_as_json(metadata):
    """
    Load configuration from environment variables as JSON

    """
    return _load_from_environ(metadata, value_func=loads)
