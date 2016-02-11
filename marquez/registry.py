"""Registry of component factories"""
from marquez.errors import AlreadyBoundError, NotBoundError


class Registry(object):
    """
    Registry of component factories.

    Supports factories registered explicitly and via entrypoints.

    """
    def __init__(self):
        self.factories = {}

    def register(self, key, factory):
        if key in self.factories:
            raise AlreadyBoundError(key)
        else:
            self.factories[key] = factory

    def resolve(self, key):
        if key in self.factories:
            return self.factories[key]
        else:
            raise NotBoundError(key)


# global registry
_registry = Registry()
