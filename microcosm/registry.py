"""
Registry of component factories.

"""
from itertools import chain
from pkg_resources import DistributionNotFound, iter_entry_points

from lazy import lazy

from microcosm.constants import DEFAULTS
from microcosm.errors import AlreadyBoundError, NotBoundError


def get_defaults(func):
    """
    Retrieve the defaults for a factory function.

    """
    return getattr(func, DEFAULTS, {})


class Registry:
    """
    Registry of component factories.

    Supports factories resolved explicitly and via entrypoints.

    """
    def __init__(self):
        self.factories = {}

    @lazy
    def entry_points(self):
        return {
            name: factory
            # NB: it's possible to have two entry points for the same name
            # (but in different distributions). This will cause unpredictable
            # behavior; don't do that.
            for name, factory in self._iter_entry_points()
        }

    @property
    def all(self):
        """
        Return a synthetic dictionary of all factories.

        """
        return {
            key: value
            for key, value in chain(self.entry_points.items(), self.factories.items())
        }

    @property
    def defaults(self):
        """
        Return a nested dicionary of all registered factory defaults.

        """
        return {
            key: get_defaults(value)
            for key, value in self.all.items()
        }

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

    def _iter_entry_points(self):
        for entry_point in iter_entry_points(group="microcosm.factories"):
            try:
                factory = entry_point.load()
            except DistributionNotFound:
                continue

            yield (entry_point.name, factory)

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

        """
        try:
            return self.entry_points[key]
        except KeyError:
            raise NotBoundError(key)


# global registry
_registry = Registry()
