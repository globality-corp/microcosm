"""
The object graph is the core unit of microcosm-based applications.

Object graphs wire together independently defined `components` using a set
of factory functions and application configuration. Components are bound
to the graph lazily (or via `graph.use()`) and are cached for reuse.

"""
from contextlib import contextmanager
from typing import Any, Iterable, Tuple

from microcosm.caching import create_cache
from microcosm.config.api import configure
from microcosm.constants import RESERVED
from microcosm.errors import CyclicGraphError, LockedGraphError
from microcosm.hooks import invoke_resolve_hook
from microcosm.loaders import load_from_environ
from microcosm.metadata import Metadata
from microcosm.profile import NoopProfiler
from microcosm.registry import _registry


class ObjectGraph:
    """
    An object graph contains all of the instantiated components for a microservice.

    Because components can reference each other acyclically, this collection of
    components forms a directed acyclic graph.

    """
    def __init__(self, metadata, config, registry, profiler, cache, loader):
        self.metadata = metadata
        self.config = config
        self._locked = False
        self._registry = registry
        self._profiler = profiler
        self._cache = cache
        self.loader = loader

    def use(self, *keys):
        """
        Explicitly initialize a set of components by their binding keys.

        """
        return [
            getattr(self, key)
            for key in keys
        ]

    def assign(self, key, value):
        """
        Explicitly assign a graph binding to a value.

        In general, graph values should only be derived from registered factories
        and the graph should not be assigned to; however, there can be exceptions including
        testing and "virtual" bindings, so assign can be used when circumventing setattr.

        """
        self._cache[key] = value
        return value

    def lock(self):
        """
        Lock the graph so that new components cannot be created.

        """
        self._locked = True
        return self

    def unlock(self):
        """
        Unlock the graph so that new components can created.

        """
        self._locked = False
        return self

    def factory_for(self, key):
        return self._registry.resolve(key)

    def get(self, key):
        return self._cache.get(key)

    def __getattr__(self, key):
        """
        Access a component by its binding key.

        If the component is not present, it will be lazily created.

        :raises CyclicGraphError: if the factory function requires a cycle
        :raises LockedGraphError: if the graph is locked

        """
        try:
            component = self._cache[key]
            if component is RESERVED:
                raise CyclicGraphError(key)
            return component
        except KeyError:
            pass

        if self._locked:
            raise LockedGraphError(key)
        return self._resolve_key(key)

    def __setattr__(self, key, value):
        if not key.startswith("_") and key not in ("metadata", "config", "loader"):
            raise Exception("Cannot setattr on ObjectGraph for key: {}".format(key))
        super(ObjectGraph, self).__setattr__(key, value)

    @contextmanager
    def _reserve(self, key):
        """
        Reserve a component's binding temporarily.

        Protects against cycles.

        """
        self.assign(key, RESERVED)
        try:
            yield
        finally:
            del self._cache[key]

    def _resolve_key(self, key):
        """
        Attempt to lazily create a component.

        :raises NotBoundError: if the component does not have a bound factory
        :raises CyclicGraphError: if the factory function requires a cycle
        :raises LockedGraphError: if the graph is locked
        """
        with self._reserve(key):
            factory = self.factory_for(key)
            with self._profiler(key):
                component = factory(self)
            invoke_resolve_hook(component)

        return self.assign(key, component)

    def items(self) -> Iterable[Tuple[str, Any]]:
        """
        Iterates over tuples of (key, component) for all bound components.
        """
        yield from self._cache.items()

    __getitem__ = __getattr__


def create_object_graph(name,
                        debug=False,
                        testing=False,
                        import_name=None,
                        root_path=None,
                        loader=load_from_environ,
                        registry=_registry,
                        profiler=None,
                        cache=None):
    """
    Create a new object graph.

    :param name: the name of the microservice
    :param debug: is development debugging enabled?
    :param testing: is unit testing enabled?
    :param loader: the configuration loader to use
    :param registry: the registry to use (defaults to the global)

    """
    metadata = Metadata(
        name=name,
        debug=debug,
        testing=testing,
        import_name=import_name,
        root_path=root_path,
    )

    defaults = registry.defaults
    config = configure(defaults, metadata, loader)

    if profiler is None:
        profiler = NoopProfiler()

    if cache is None or isinstance(cache, str):
        cache = create_cache(cache)

    return ObjectGraph(
        metadata=metadata,
        config=config,
        registry=registry,
        profiler=profiler,
        cache=cache,
        loader=loader,
    )
