"""
The object graph is the core unit of microcosm-based applications.

Object graphs wire together independently defined `components` using a set
of factory functions and application configuration. Components are bound
to the graph lazily (or via `graph.use()`) and are cached for reuse.

"""
from __future__ import annotations

from collections.abc import Callable, Iterable
from contextlib import contextmanager
from typing import Any

from microcosm.caching import Cache, create_cache
from microcosm.config.api import configure
from microcosm.config.model import Configuration
from microcosm.constants import RESERVED
from microcosm.errors import CyclicGraphError, LockedGraphError
from microcosm.hooks import invoke_resolve_hook
from microcosm.loaders import load_from_environ
from microcosm.metadata import Metadata
from microcosm.profile import NoopProfiler
from microcosm.registry import Registry, _registry
from microcosm.typing import Component


Factory = Callable[['ObjectGraph'], Component]


class ObjectGraph:
    """
    An object graph contains all of the instantiated components for a microservice.

    Because components can reference each other a-cyclically, this collection of
    components forms a directed acyclic graph.

    """
    def __init__(self, metadata: Metadata, config, registry, profiler, cache, loader) -> None:
        self.metadata = metadata
        self.config = config
        self._locked = False
        self._registry = registry
        self._profiler = profiler
        self._cache = cache
        self.loader = loader

    def use(self, *keys: str) -> list[Component]:
        """
        Explicitly initialize a set of components by their binding keys.

        """
        return [getattr(self, key) for key in keys]

    def assign(self, key: str, value: Component) -> Component:
        """
        Explicitly assign a graph binding to a value.

        In general, graph values should only be derived from registered factories
        and the graph should not be assigned to; however, there can be exceptions including
        testing and "virtual" bindings, so assign can be used when circumventing setattr.

        """
        self._cache[key] = value
        return value

    def lock(self) -> ObjectGraph:
        """
        Lock the graph so that new components cannot be created.

        """
        self._locked = True
        return self

    def unlock(self) -> ObjectGraph:
        """
        Unlock the graph so that new components can created.

        """
        self._locked = False
        return self

    def factory_for(self, key: str) -> Factory:
        return self._registry.resolve(key)

    def get(self, key: str) -> Component:
        return self._cache.get(key)

    def __getattr__(self, key: str) -> Component:
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

    def __setattr__(self, key: str, value: Component) -> None:
        if not key.startswith("_") and key not in ("metadata", "config", "loader"):
            raise Exception(f"Cannot setattr on ObjectGraph for key: {key}")
        super().__setattr__(key, value)

    @contextmanager
    def _reserve(self, key: str) -> Any:
        """
        Reserve a component's binding temporarily.

        Protects against cycles.

        """
        self.assign(key, RESERVED)
        try:
            yield
        finally:
            del self._cache[key]

    def _resolve_key(self, key: str) -> Component:
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

    def items(self) -> Iterable[tuple[str, Component]]:
        """
        Iterates over tuples of (key, component) for all bound components.
        """
        yield from self._cache.items()

    __getitem__ = __getattr__


def create_object_graph(
    name: str,
    debug: bool = False,
    testing: bool = False,
    import_name: str | None = None,
    root_path: str | None = None,
    loader: Callable[[Metadata], Configuration] = load_from_environ,
    registry: Registry = _registry,
    profiler: Any = None,
    cache: type[Cache] | None = None,
    description: str = "",
) -> ObjectGraph:
    """
    Create a new object graph.

    :param name: the name of the microservice
    :param debug: is development debugging enabled?
    :param testing: is unit testing enabled?
    :param import_name: the import name to use for resource loading
    :param root_path: the root path for resource loading
    :param loader: the configuration loader to use
    :param registry: the registry to use (defaults to the global)
    :param profiler:
    :param cache:
    :param description: an informative description of the graph object

    """
    metadata = Metadata(
        name=name,
        debug=debug,
        testing=testing,
        import_name=import_name,
        root_path=root_path,
        description=description,
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


def get_component_name(graph: ObjectGraph, component: Component) -> str:
    """
    Given an object that is attached to the graph, it returns the object name.

    """
    return next(
        key
        for key, possible_component in graph.items()
        if possible_component == component
    )
