"""
Configuration loading

A configuration loader is any function that accepts `Metadata` and
returns a `Configuration` object or equivalent dict.

Configuration might be loaded from a file, from environment variables,
or from an external service.

"""
from json import loads
from os import environ

from inflection import underscore

from microcosm.configuration import Configuration


def expand_config(dct,
                  separator='.',
                  key_func=lambda key: key.lower(),
                  key_parts_filter=lambda key_parts: True,
                  value_func=lambda value: value):
    """
    Expand a dictionary recursively by splitting keys along the separator.

    :param dct: a non-recursive dictionary
    :param separator: a separator charactor for splitting dictionary keys
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
        for key_part in key_parts[1:-1]:
            key_config = key_config.setdefault(key_func(key_part), dict())
        key_config[key_func(key_parts[-1])] = value_func(value)

    return config


def get_config_filename(metadata):
    """
    Derive a configuration file name from the FOO_SETTINGS
    environment variable.

    """
    envvar = "{}__SETTINGS".format(underscore(metadata.name).upper())
    try:
        return environ[envvar]
    except KeyError:
        return None


def _load_from_file(metadata, load_func):
    """
    Load configuration from a file.

    The file path is derived from an environment variable
    named after the service of the form FOO_SETTINGS.

    """
    config_filename = get_config_filename(metadata)
    if config_filename is None:
        return Configuration()

    with open(config_filename, "r") as file_:
        data = load_func(file_.read())
        return Configuration(data)


def load_from_json_file(metadata):
    """
    Load configuration from a JSON file.

    """
    return _load_from_file(metadata, loads)


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


def load_from_dict(dct=None, **kwargs):
    """
    Load configuration from a dictionary.

    """
    dct = dct or dict()
    dct.update(kwargs)

    def _load_from_dict(metadata):
        return Configuration(dct)
    return _load_from_dict


def load_each(*loaders):
    """
    Loader factory that combines a series of loaders.

    """
    def _load_each(metadata):
        config = loaders[0](metadata)
        for loader in loaders[1:]:
            next_config = loader(metadata)
            config.merge(next_config)
        return config
    return _load_each
