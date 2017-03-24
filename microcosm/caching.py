"""
Component caches.

The object graph caches components to avoid repeated factory calls.

Alternate cache implementations can be used to speed up performance
(or to force re-creation).

"""
from abc import ABCMeta, abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class Cache(object):
    """
    A cache uses the basic dictionary interface and defines a name.

    """

    @classmethod
    def name(self):
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, name):
        pass

    @abstractmethod
    def __setitem__(self, name, component):
        pass

    @abstractmethod
    def __delitem__(self, name):
        pass


class NaiveCache(dict, Cache):
    """
    Cache components in a dictionary.

    Under most circumstances, every instantiation of an object graph
    results in a new `NaiveCache` and a new instantitation of components.

    Most applications will want a `NaiveCache` for "real" usage.

    """
    @classmethod
    def name(self):
        return "naive"


class ProcessCache(Cache):
    """
    Cache components in process state.

    Reuses components if they have been instantiated in the same process
    (even if object graph configuration has changed).

    Under many testing circumstances, component reuse saves instantitation
    time (at the expense of a "clean slate" testing context).

    """
    CACHE = dict()

    @classmethod
    def name(self):
        return "process"

    def __getitem__(self, name):
        return ProcessCache.CACHE[name]

    def __setitem__(self, name, component):
        ProcessCache.CACHE[name] = component

    def __delitem__(self, name):
        del ProcessCache.CACHE[name]


def create_cache(name):
    """
    Create a cache by name.

    Defaults to `NaiveCache`

    """
    caches = {
        subclass.name(): subclass
        for subclass in Cache.__subclasses__()
    }
    return caches.get(name, NaiveCache)()
