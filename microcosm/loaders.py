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
    def load_python_module(data):
        module = new_module("magic")
        exec data in module.__dict__, module.__dict__
        return {
            key: value
            for key, value in module.__dict__.items()
            if not key.startswith("_")
        }
    return _load_from_file(metadata, load_python_module)
