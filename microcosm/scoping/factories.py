"""
A factory that enables scoping.

"""
from microcosm.config.api import configure
from microcosm.config.model import Configuration
from microcosm.object_graph import Factory, ObjectGraph
from microcosm.registry import get_defaults
from microcosm.scoping.object_graph import ScopedGraph
from microcosm.scoping.proxies import ScopedProxy
from microcosm.typing import Component


class ScopedFactory:
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
    def __init__(self, key: str, func: Factory, default_scope=None):
        self.key = key
        self.func = func
        self.current_scope = default_scope
        self.default_scope = default_scope

    @property
    def scoped_key(self):
        # NB: deliberately conflating false-y values
        return "{}.{}".format(self.current_scope or "", self.key)

    def get_scoped_config(self, graph: ObjectGraph) -> Configuration:
        """
        Compute a configuration using the current scope.

        """
        def loader(metadata):
            if not self.current_scope:
                target = graph.config
            else:
                target = graph.config.get(self.current_scope, {})
            return {
                self.key: target.get(self.key, {}),
            }

        defaults = {
            self.key: get_defaults(self.func),
        }
        return configure(defaults, graph.metadata, loader)

    def __call__(self, graph: ObjectGraph) -> ScopedProxy:
        """
        Override component creation to use scoped config.

        """
        self.resolve(graph)
        return ScopedProxy(graph, self)

    def resolve(self, graph: ObjectGraph) -> Component:
        """
        Resolve a scoped component, respecting the graph cache.

        """
        cached = graph.get(self.scoped_key)
        if cached:
            return cached

        component = self.create(graph)
        graph.assign(self.scoped_key, component)
        return component

    def create(self, graph: ObjectGraph) -> Component:
        """
        Create a new scoped component.

        """
        scoped_config = self.get_scoped_config(graph)
        scoped_graph = ScopedGraph(graph, scoped_config)
        return self.func(scoped_graph)

    @classmethod
    def infect(cls, graph: ObjectGraph, key: str, default_scope=None) -> Factory:
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
