"""
Factory decorators

"""
from collections.abc import Callable

from microcosm.constants import DEFAULTS
from microcosm.registry import Registry, _registry


def binding(key: str, registry: Registry | None = None) -> Callable[..., None]:
    """
    Creates a decorator that binds a factory function to a key.

    :param key: the binding key
    :param registry: the registry to bind to; defaults to the global registry

    """
    if registry is None:
        registry = _registry

    def decorator(func):
        registry.bind(key, func)  # type: ignore[union-attr]
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
