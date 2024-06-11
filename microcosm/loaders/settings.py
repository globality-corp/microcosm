"""
Load configuration from a settings file.

The settings file is identified using a `FOO_SETTINGS` environment variable
and consumed using a customizable load function (default: json).

"""
from collections.abc import Callable, Mapping
from json import loads
from os import environ
from typing import Any

from inflection import underscore

from microcosm.metadata import Metadata


def get_config_filename(metadata: Metadata) -> str | None:
    """
    Derive a configuration file name from the FOO_SETTINGS
    environment variable.

    """
    envvar = f"{underscore(metadata.name).upper()}__SETTINGS"
    try:
        return environ[envvar]
    except KeyError:
        return None


def _load_from_file(metadata: Metadata, load_func: Callable[[str], Mapping[str, str]]) -> dict[Any, Any]:
    """
    Load configuration from a file.

    The file path is derived from an environment variable
    named after the service of the form FOO_SETTINGS.

    """
    config_filename = get_config_filename(metadata)
    if config_filename is None:
        return dict()

    with open(config_filename) as file_:
        data = load_func(file_.read())
        return dict(data)


def load_from_json_file(metadata: Metadata) -> dict[Any, Any]:
    """
    Load configuration from a JSON file.

    """
    return _load_from_file(metadata, loads)
