"""Registry of component factories"""
from pkg_resources import iter_entry_points

from marquez.errors import AlreadyBoundError, NotBoundError


class Registry(object):
    """
    Registry of component factories.

    Supports factories resolved explicitly and via entrypoints.

    """
    def __init__(self):
        self.factories = {}

    def bind(self, key, factory):
        """
        Bind a factory to a key.

        :raises AlreadyBoundError: if the key is alrady bound

        """
        if key in self.factories:
            raise AlreadyBoundError(key)
        else:
            self.factories[key] = factory

    def resolve(self, key):
        """
        Resolve a key to a factory.

        Attempts to resolve explicit bindings and entry points, preferring
        explicit bindings.

        :raises NotBoundError: if the key cannot be resolved

        """
        try:
            return self._resolve_from_binding(key)
        except NotBoundError:
            return self._resolve_from_entry_point(key)

    def _resolve_from_binding(self, key):
        """
        Resolve using bindings.

        """
        try:
            return self.factories[key]
        except KeyError:
            raise NotBoundError(key)

    def _resolve_from_entry_point(self, key):
        """
        Resolve using entry points.

        If there are multiple entry point bindings exist for the key, resolution
        order is arbitray; so don't do that.

        """
        for entry_point in iter_entry_points(group="marquez.factories", name=key):
            return entry_point.load()
        else:
            raise NotBoundError(key)


# global registry
_registry = Registry()
