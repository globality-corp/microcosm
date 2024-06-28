"""
Opaque context data for communicating between service layers.

The `graph.opaque` value is a dictionary-like object that can contain arbitrary data.
Within different kinds of application logic, this value may be populated with different
kinds of context, notably:

 -  An input web request might extract values from request HTTP headers (see `microcosm-flask`)
 -  A pubsub framework might extract values from inbound message metadata (see `microcosm-pubsub`)

Similarly, different layers of an application may use this data in different ways:

 -  A logging decorator might automatically log all opaque values (see `microcosm-logging`)
 -  A pubsub framework might insert opaque values into new messages (see `microcosm-pubsub`)
 -  An outbound web request might insert opaque values as HTTP headers

Combining opaque data across an entire fleet of services allows for consistent tracing and
easier debugging of distributed operations.

"""
from collections.abc import MutableMapping
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy


class NormalizedDict(dict):  # type: ignore[type-arg]
    """
    Dict where all str keys are lowercase and read methods are case-insensitive.

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in list(self.keys()):
            value = super().pop(key)
            self[key] = value

    def __setitem__(self, key, value):
        super().__setitem__(self._convert_key(key), value)

    def __getitem__(self, key):
        return super().__getitem__(self._convert_key(key))

    def __delitem__(self, key):
        super().__delitem__(self._convert_key(key))

    def __contains__(self, key):
        return super().__contains__(self._convert_key(key))

    def pop(self, key, *args, **kwargs):
        return super().pop(self._convert_key(key), *args, **kwargs)

    def get(self, key, *args, **kwargs):
        return super().get(self._convert_key(key), *args, **kwargs)

    def update(self, *args, **kwargs):
        for key, value in dict(*args, **kwargs).items():
            self[key] = value

    def setdefault(self, key, *args, **kwargs):
        super().setdefault(self._convert_key(key), *args, **kwargs)

    @classmethod
    def fromkeys(cls, keys, v=None):
        keys = (
            cls._convert_key(key)
            for key in keys
        )
        return super().fromkeys(keys, v)

    @staticmethod
    def _convert_key(key):
        return key.casefold() if isinstance(key, str) else key


def _make_initializer(opaque):
    @contextmanager
    def initialiser(func, *args, **kwargs):
        token = opaque._store.set(deepcopy(opaque._store.get()))
        opaque.update(func(*args, **kwargs))
        try:
            yield
        finally:
            opaque._store.reset(token)

    return initialiser


class Opaque(MutableMapping[str, str]):
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

    def __init__(self, *args, **kwargs) -> None:
        self.service_name: str | None = kwargs.pop("name", None)
        self._store = ContextVar("store", default=NormalizedDict(*args, **kwargs))
        self.initialize = _make_initializer(self)

    def __getitem__(self, key):
        return self._store.get()[key]

    def __setitem__(self, key, value):
        self._store.get()[key] = value

    def __delitem__(self, key):
        del self._store.get()[key]

    def __iter__(self):
        return iter(self._store.get())

    def __len__(self):
        return len(self._store.get())

    def as_dict(self):
        return self._store.get()


def configure_opaque(graph) -> Opaque:
    return Opaque(graph.config.opaque, name=graph.metadata.name)
