"""
Component caches.

The object graph caches components to avoid repeated factory calls.

Alternate cache implementations can be used to speed up performance
(or to force re-creation).

"""
from collections import defaultdict
from collections.abc import MutableMapping
from typing import Any, Mapping


class Cache(MutableMapping):
    """
    A cache supports the basic dictionary interface and defines a name.

    """
    @classmethod
    def name(self):
        raise NotImplementedError


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

    def __getitem__(self, name):
        return ProcessCache.CACHES[self.scope][name]

    def __setitem__(self, name, component):
        ProcessCache.CACHES[self.scope][name] = component

    def __delitem__(self, name):
        del ProcessCache.CACHES[self.scope][name]

    def __iter__(self):
        return iter(ProcessCache.CACHES[self.scope])

    def __len__(self):
        return len(ProcessCache.CACHES[self.scope])


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
