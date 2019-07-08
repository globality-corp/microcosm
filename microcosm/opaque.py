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
from collections import MutableMapping
from contextlib import ContextDecorator, ExitStack
from copy import deepcopy
from types import MethodType

from opentracing_instrumentation.request_context import span_in_context


def _make_initializer(opaque):

    class OpaqueInitializer(ContextDecorator, ExitStack):
        def __init__(self, func, *args, **kwargs):
            super().__init__()

            def member_func(self):
                return func(*args, **kwargs)

            self.func = MethodType(member_func, self)
            self.saved = None

        def __enter__(self):
            self.saved = deepcopy(opaque._store)
            opaque.update(self.func())

            if opaque.tracer:
                span = self.enter_context(opaque.tracer.start_span(opaque.name))
                for key, value in opaque.as_dict().items():
                    span.set_tag(key, value)
                # make sure the span is passed down along functions
                self.enter_context(span_in_context(span))

        def __exit__(self, *exc):
            opaque._store = self.saved
            self.saved = None
            super().__exit__(*exc)

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
        self.tracer = kwargs.pop("tracer", None)
        self.name = kwargs.pop("name", "opaque")
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
    return Opaque(graph.config.opaque, tracer=graph.tracer, name=graph.metadata.name)
