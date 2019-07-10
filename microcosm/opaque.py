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

from opentracing.ext import tags
from opentracing.propagation import Format
from opentracing_instrumentation.request_context import span_in_context

from microcosm.tracing import SPAN_NAME


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

            # Use of a tracing solution on top of opaque is optional!
            if opaque.tracer:
                span = self.start_span()
                self.set_tags(span)
                self.pass_span_context_to_children(span)

        def start_span(self):
            """
            Extract any existing span context from the graph, and use it to
            initialize a span for this opaque context.
            """
            span_context = opaque.tracer.extract(Format.TEXT_MAP, opaque.as_dict())
            span_tags = {tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER}

            return self.enter_context(
                opaque.tracer.start_span(
                    opaque.get(SPAN_NAME, opaque.service_name),
                    child_of=span_context,
                    tags=span_tags,
                ),
            )

        def set_tags(self, span):
            """
            Copy opaque tags into tracer tags.
            """
            for key, value in opaque.as_dict().items():
                span.set_tag(key, value)

        def pass_span_context_to_children(self, span):
            """
            Save span information in jaeger global storage as well as in
            graph.opaque so it can be passed to children in this process as
            well as across other processes e.g. over HTTP calls or pubsub
            boundaries.

            """
            self.enter_context(span_in_context(span))
            span_dict = dict()
            opaque.tracer.inject(span, Format.HTTP_HEADERS, span_dict)
            opaque.update(span_dict)

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
        self.service_name = kwargs.pop("name", None)
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
