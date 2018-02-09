"""
Factory decorators

"""
from microcosm.registry import _registry


DEFAULTS = "_defaults"


def binding(key, registry=None):
    """
    Creates a decorator that binds a factory function to a key.

    :param key: the binding key
    :param: registry: the registry to bind to; defaults to the global registry

    """
    if registry is None:
        registry = _registry

    def decorator(func):
        registry.bind(key, func)
        return func
    return decorator


def defaults(**kwargs):
    """
    Creates a decorator that saves the provided kwargs as defaults for a factory function.

    """
    def decorator(func):
        setattr(func, DEFAULTS, kwargs)
        return func
    return decorator


def get_defaults(func):
    """
    Retrieve the defaults for a factory function.

    """
    return getattr(func, DEFAULTS, {})


def iter_keys(dct, prefix=""):
    for key, value in dct.items():
        if isinstance(value, dict):
            yield from iter_keys(value, f"{key}.")
        else:
            yield f"{prefix}{key}"


def public(loader):
    """
    Flag a loader as non-secret.

    """
    def load(metadata):
        data = loader(metadata)
        for key in iter_keys(data):
            metadata.keys["public"].add(key)
        return data
    return load
