from contextdecorator import ContextDecorator
from collections import MutableMapping
from copy import deepcopy
from types import MethodType

from microcosm.api import binding


class Opaque(MutableMapping):
    """
    The Opaque collaborator and its assocaited context manager are extremely useful for
    instantiating context specific data during transaction processing. Example:

        from microcosm.opaque import Opaque

        # set up
        def special_opaque_data(some, stuff):
            return "{} {}".format(some, stuff)
        some = "some"
        stuff = "stuff"

        opaque = Opaque()

        # usage
        print opaque.opaque_data_func()

        with opaque.opaque_data(special_opaque_data, some, stuff):
            print opaque.opaque_data_func()

        print opaque.opaque_data_func()

    Outputs:

        {}
        some stuff
        {}


    Note: opaque.opaque_data may also be used as a decorator.

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

    def _default_data_func(self):
        return {}

    def as_dict(self):
        return self._store


def _make_bind(opaque):
    class OpaqueData(ContextDecorator):
        def __init__(self, opaque_data_func, *args, **kwargs):
            self.original_store = deepcopy(opaque._store)

            def context_specific_data_func(self):
                return opaque_data_func(*args, **kwargs)
            self.context_specific_data_func = MethodType(context_specific_data_func, self)

        def __enter__(self):
            opaque.update(self.context_specific_data_func())

        def __exit__(self, *exc):
            opaque._store = self.original_store
    return OpaqueData


@binding("opaque")
def configure_opaque(graph):
    return Opaque()
