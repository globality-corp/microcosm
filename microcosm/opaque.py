from contextdecorator import ContextDecorator
from collections import MutableMapping
from copy import deepcopy
from types import MethodType

from microcosm.api import binding


class Opaque(MutableMapping):
    """
    The Opaque collaborator and its associated context manager/decorator are
    useful for instantiating context specific data during transaction processing.
    Opaque.bind(func, *args, **kwargs) can be used as both a decorator and a
    context manager to set opaque to a dict-like object updated with the dictionary
    returned by func(*args, **kwargs) whose value will be reset after the decorator/context
    manager exits.

    See tests for usage examples.

    """
    def __init__(self, *args, **kwargs):
        self._store = dict()
        self.update(dict(*args, **kwargs))
        self.bind = _make_bind(self)

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        del self._store[key]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def as_dict(self):
        return self._store


def _make_bind(opaque):
    class OpaqueData(ContextDecorator):
        def __init__(self, opaque_data_func, *args, **kwargs):

            def context_specific_data_func(self):
                return opaque_data_func(*args, **kwargs)

            self.context_specific_data_func = MethodType(context_specific_data_func, self)

        def __enter__(self):
            self.original_store = deepcopy(opaque._store)
            opaque.update(self.context_specific_data_func())

        def __exit__(self, *exc):
            opaque._store = self.original_store
    return OpaqueData


@binding("opaque")
def configure_opaque(graph):
    return Opaque()
