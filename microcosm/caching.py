"""
Component caches.

The object graph caches components to avoid repeated factory calls.

Alternate cache implementations can be used to speed up performance
(or to force re-creation).

"""
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import Mapping, Any


class Cache(metaclass=ABCMeta):
    """
    A cache uses the basic dictionary interface and defines a name.

    """
    @classmethod
    def name(self):
        raise NotImplementedError

    @abstractmethod
    def __contains__(self, name):
        pass

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
    CACHES: Mapping[str, Mapping[str, Any]] = defaultdict(dict)

    @classmethod
    def name(self):
        return "process"

    def __init__(self, scope="default"):
        self.scope = scope

    def __contains__(self, name):
        return name in ProcessCache.CACHES[self.scope]

    def get(self, name):
        return self.__getitem__(name)

    def __getitem__(self, name):
        return ProcessCache.CACHES[self.scope][name]

    def __setitem__(self, name, component):
        ProcessCache.CACHES[self.scope][name] = component

    def __delitem__(self, name):
        del ProcessCache.CACHES[self.scope][name]


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
