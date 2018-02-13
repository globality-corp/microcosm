"""
Configuration API.

"""
from microcosm.config.model import Configuration
from microcosm.decorators import DEFAULTS


def get_defaults(func):
    """
    Retrieve the defaults for a factory function.

    """
    return getattr(func, DEFAULTS, {})


def configure(registry, metadata, loader):
    """
    Build a fresh configuration.

    """
    config = Configuration({
        key: get_defaults(value)
        for key, value in registry.all.items()
    })
    config.merge(loader(metadata))
    return config


def configure_scoped(graph, key, factory, loader):
    """
    Build a sub-configuration for a specific binding.

    :params key: a binding key
    """
    config = Configuration({
        key: get_defaults(factory),
    })
    config.merge(loader(graph.metadata))
    return config
