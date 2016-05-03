"""
Configuration loading

A configuration loader is any function that accepts `Metadata` and
returns a `Configuration` object. Configuration might be loaded
from a file, from environment variables, or from an external service.
"""
from imp import new_module
from json import loads
from os import environ

from inflection import underscore

from microcosm.configuration import Configuration


def get_config_filename(metadata):
    """
    Derive a configuration file name from the FOO_SETTINGS
    environment variable.

    """
    envvar = "{}_SETTINGS".format(underscore(metadata.name).upper())
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


def load_from_python_file(metadata):
    """
    Load configuration from a Python file.

    The file path is derived from an environment variable
    named after the service of the form FOO_SETTINGS.

    """
    return _load_from_file(metadata, _load_python_module)


def _load_python_module(data):
    module = new_module("magic")
    exec(data, module.__dict__, module.__dict__)
    return {
        key: value
        for key, value in module.__dict__.items()
        if not key.startswith("_")
    }


def _load_from_environ(metadata, value_func=None):
    """
    Load configuration from environment variables.

    Any environment variable prefixed with the metadata's name will be
    used to recursively set dictionary keys, splitting on '_' or '__'.

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

    prefix = metadata.name.upper().replace("-", "_").split("_")

    def matches_app(key_parts):
        return len(key_parts) > len(prefix) and key_parts[:len(prefix)] == prefix

    def assign_value(dct, key, value):
        dct[key.lower()] = value_func(value) if value_func else value

    def process_env_var(key_parts, value, config):
        if not matches_app(key_parts):
            return
        dct = config
        # walk the path specified by the env var to put the value in the right
        # place in the config
        for key_part in key_parts[len(prefix):-1]:
            if key_part.lower() not in dct:
                dct[key_part.lower()] = dict()
            dct = dct[key_part.lower()]
        assign_value(dct, key_parts[-1], value)

    config = Configuration()
    for key, value in environ.items():
        separator = "__" if "__" in key else "_"
        key_parts = key.split(separator)
        process_env_var(key_parts, value, config)
    return config


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
