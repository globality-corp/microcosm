"""
Configuration loading

A configuration loader is any function that accepts `Metadata` and
returns a `dict` (or `Configuration` model).

Configuration might be loaded from a file, from environment variables,
or from an external service.

"""
from microcosm.config.model import Configuration
from microcosm.loaders.compose import load_each, two_stage_loader  # noqa: F401
from microcosm.loaders.environment import (  # noqa: F401
    load_from_environ,
    load_from_environ_as_json,
)
from microcosm.loaders.keys import expand_config  # noqa: F401
from microcosm.loaders.settings import load_from_json_file  # noqa: F401
from microcosm.metadata import Metadata


def load_from_dict(dct=None, **kwargs):
    """
    Load configuration from a dictionary.

    """
    dct = dct or dict()
    dct.update(kwargs)

    def _load_from_dict(metadata):
        return Configuration(dct)
    return _load_from_dict


def empty_loader(metadata: Metadata):
    return Configuration()
