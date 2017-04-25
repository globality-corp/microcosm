"""
Opaque context data for communicating between service layers.

The `graph.opaque` value is a dictionary-like object that can contain arbitrary data.
Within different kinds of application logic, this value may be populated with different
kinds of context, notably:

 -  An input web request might extract values from request HTTP headers (see `microcosm-flask`)
 -  A pubsub framework might extract values from inbound message metadata (see `microcosm-pubsub`)

Similarly, different layers of an application may use this data in different ways:

 -  A logging decoratory might automatically log all opaque values (see `microcosm-logging`)
 -  A pubsub framework might insert opaque values into new messages (see `microcosm-pubsub`)
 -  An outbound web request might insert opaque values as HTTP headers

Combining opaque data across an entire fleet of services allows for consistent tracing and
easier debugging of distributed operations.

"""
from contextdecorator import ContextDecorator
from collections import MutableMapping
from copy import deepcopy
from types import MethodType


def _make_initializer(opaque):

    class OpaqueInitializer(ContextDecorator):
        def __init__(self, func, *args, **kwargs):

            def member_func(self):
                return func(*args, **kwargs)

            self.func = MethodType(member_func, self)
            self.saved = None

        def __enter__(self):
            self.saved = deepcopy(opaque._store)
            opaque.update(self.func())

        def __exit__(self, *exc):
            opaque._store = self.saved
            self.saved = None

    return OpaqueInitializer


class Opaque(MutableMapping):
    """
    Define a dict-like opaque context that can be initialized with application-specific values.

    Exposes a context manager/decorator interface that takes a generic function:

        opaque.initialize(func, *args, **kwargs)

    Or:

        with opaque.initialize(func, *args, **kwargs):
            pass

    Or:

        @opaque.initialize(func, *args, **kwargs)
        def foo():
            pass

    See tests for usage examples.

    """
    def __init__(self, *args, **kwargs):
        self._store = dict(*args, **kwargs)
        self.initialize = _make_initializer(self)

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


def configure_opaque(graph):
    return Opaque(graph.config.opaque)
