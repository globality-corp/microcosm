"""
Configuration API.

"""
from microcosm.config.model import Configuration
from microcosm.config.validation import validate


def configure(defaults, metadata, loader):
    """
    Build a fresh configuration.

    :params defaults: a nested dictionary of keys and their default values
    :params metadata: the graph metadata
    :params loader: a configuration loader

    """
    config = Configuration(defaults)
    config.merge(loader(metadata))
    validate(defaults, metadata, config)
    return config
