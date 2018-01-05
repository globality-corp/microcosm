"""
Service metadata

"""
from os.path import abspath, dirname, join
from sys import modules


class Metadata:
    """
    Service metadata.

    Factories should use service metadata to implement conventions.

    """

    def __init__(self, name, debug=False, testing=False, import_name=None, root_path=None):
        """
        :param name: the name of the microservice
        :param debug: is development debugging enabled?
        :param testing: is unit testing enabled?
        :param import_name: the import name to use for resource loading
        :param root_path: the root path for resource loading

        """
        self.name = name
        self.debug = debug
        self.testing = testing
        self.import_name = import_name or self.name
        self.root_path = root_path or self.get_root_path(self.import_name)

    def get_root_path(self, name):
        """
        Attempt to compute a root path for a (hopefully importable) name.

        Based in part on Flask's `root_path` calculation. See:

            https://github.com/mitsuhiko/flask/blob/master/flask/helpers.py#L777

        """
        module = modules.get(name)
        if module is not None and hasattr(module, '__file__'):
            return dirname(abspath(module.__file__))

        # Flask keeps looking at this point. We instead set the root path to None,
        # assume that the user doesn't need resource loading, and raise an error
        # when resolving the resource path.
        return None

    def get_path(self, path):
        if self.root_path is None:
            raise RuntimeError("Root path was not defined. Either use a resolvable name or set root path explicitly.")
        return join(self.root_path, path)
