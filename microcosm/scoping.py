"""
Scope bindings to multiple configurations.

This feature is EXPERIMENTAL! Use at your own risk.

"""
from contextlib import contextmanager
from functools import wraps

from microcosm.configuration import Configuration
from microcosm.decorators import get_defaults
from microcosm.registry import _registry


class ScopedGraph(object):

    def __init__(self, graph, config):
        self._graph = graph
        self.config = config
        self.metadata = graph.metadata

    def __getattr__(self, key):
        return getattr(self._graph, key)


def scoped_binding(key, default_scope=None, registry=_registry):
    def decorator(func):
        registry.bind(key, ScopedFactory(key, func, default_scope))
        return func
    return decorator


class ScopedProxy(object):

    def __init__(self, graph, factory):
        self.graph = graph
        self.factory = factory

    def __call__(self, *args, **kwargs):
        return self.factory.create(self.graph)(*args, **kwargs)

    def __getattr__(self, attr):
        return getattr(self.factory.create(self.graph), attr)

    @contextmanager
    def scoped_to(self, scope):
        """
        Context manager to switch scopes.

        """
        previous_scope = self.factory.current_scope
        try:
            self.factory.current_scope = scope
            yield
        finally:
            self.factory.current_scope = previous_scope

    def scoped(self, func):
        """
        Decorator to switch scopes.

        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            scope = kwargs.get("scope", self.factory.default_scope)
            with self.scoped_to(scope):
                return func(*args, **kwargs)
        return wrapper


class ScopedFactory(object):
    """
    A factory bound to a scoped config key.

    Allows the same binding key (`foo`) to be used to refer to multiple instances
    of the factory-generated component using different configurations.

    For example, this configuration:

        {
           "foo": {
              "host": "host1",
           },
           "bar": {
              "foo": {
                 "host": "host2",
              },
           },
        }

    Could be used with the same underlying factory to refer to either "host1" or "host2"
    depending on the current scope.

    """
    def __init__(self, key, func, default_scope=None):
        self.key = key
        self.func = func
        self.current_scope = default_scope
        self.default_scope = default_scope

        # cache instances here instead of in the graph cache
        self.cache = {}

    @property
    def no_cache(self):
        """
        Disable graph caching.

        """
        return True

    def get_scoped_config(self, graph):
        """
        Compute a configuration using the current scope.

        """
        # start with the factory's defaults
        config = Configuration({
            self.key: get_defaults(self.func),
        })

        # merge in the appropriate config
        if self.current_scope is None:
            target_config = graph.config
        else:
            target_config = graph.config.get(self.current_scope, {})

        config.merge({
            self.key: target_config.get(self.key, {}),
        })
        return config

    def __call__(self, graph):
        """
        Override component creation to use scoped config.

        """
        self.create(graph)
        return ScopedProxy(graph, self)

    def create(self, graph):
        if self.current_scope in self.cache:
            return self.cache[self.current_scope]

        scoped_config = self.get_scoped_config(graph)
        scoped_graph = ScopedGraph(graph, scoped_config)

        component = self.func(scoped_graph)
        self.cache[self.current_scope] = component
        return component

    @classmethod
    def infect(cls, graph, key, default_scope=None):
        """
        Forcibly convert an entry-point based factory to a ScopedFactory.

        Must be invoked before resolving the entry point.

        :raises AlreadyBoundError: for non entry-points; these should be declared with @scoped_binding

        """
        func = graph.factory_for(key)
        if isinstance(func, cls):
            func = func.func
        factory = cls(key, func, default_scope)
        graph._registry.factories[key] = factory
        return factory
