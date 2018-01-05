"""
A view of the object graph that exposes only a subset of configuration.

"""


class ScopedGraph:

    def __init__(self, graph, config):
        self._graph = graph
        self.config = config
        self.metadata = graph.metadata

    def __getattr__(self, key):
        return getattr(self._graph, key)
