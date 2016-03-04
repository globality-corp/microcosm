"""
Allows object graph members to be imported by defining custom finders and loaders.

"""
from imp import new_module
import sys


class ModuleFinder(object):
    """
    A module "finder" that matches a configured package name.
    """
    def __init__(self, graph, package_name):
        """
        :param graph: the object graph
        :param package_name: the package name
        """
        self.graph = graph
        self.package_name = package_name

    def find_module(self, fullname, path=None):
        if self.package_name.startswith(fullname):
            return ModuleLoader(self.graph, self.package_name)
        else:
            return None

    @classmethod
    def export(cls, graph, package_name):
        module_finder = cls(
            graph,
            package_name,
        )
        sys.meta_path.append(module_finder)


class ModuleLoader(object):
    """
    A module "loader" that returns object graph components.
    """
    def __init__(self, graph, package_name):
        """
        :param graph: the object graph
        :param package_name: the package name prefix
        """
        self.graph = graph
        self.package_name = package_name

    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]

        module = self.make_module(fullname)
        sys.modules[fullname] = module

        if fullname == self.package_name:
            module.__dict__.update(self.graph._components)

        return module

    def make_module(self, fullname):
        module = new_module(fullname)
        module.__file__ = "<microcosm>"
        module.__loader__ = self
        module.__package__ = fullname
        module.__path__ = []
        return module
