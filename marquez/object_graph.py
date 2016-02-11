"""Object Graph"""
from marquez.configuration import Configuration
from marquez.decorators import get_defaults
from marquez.loaders import load_from_python_file
from marquez.metadata import Metadata
from marquez.registry import _registry


class ObjectGraph(object):
    """
    An object graph contains all of the instantiated components for a microservice.

    Because components can reference each other acyclically, this collection of
    components forms a directed acyclic graph.

    """
    def __init__(self, metadata, config, registry):
        self.metadata = metadata
        self.config = config
        self._registry = registry
        self._components = {}

    def __getattr__(self, key):
        """
        Access a component by its binding key.

        If the component is not present, it will be lazily created.

        """
        try:
            return self._components[key]
        except KeyError:
            return self._resolve_key(key)

    def _resolve_key(self, key):
        """
        Attempt to lazily create a component.

        :raises NotBoundError: if the component does not have a bound factory
        """
        factory = self._registry.resolve(key)
        self._components[key] = component = factory(self)
        return component


def create_object_graph(name, debug=False, testing=False, loader=load_from_python_file, registry=_registry):
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
    )

    config = Configuration({
        key: get_defaults(value)
        for key, value in registry.all.items()
    })
    config.merge(loader(metadata))

    return ObjectGraph(
        metadata=metadata,
        config=config,
        registry=registry,
    )
