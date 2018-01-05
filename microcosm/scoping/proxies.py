"""
A component proxy that is scoping aware.

The scope can be set in one of two ways:

    # as a context manager that dervices the scope explicitly
    with graph.foo.scoped_to("myscope"):
        graph.foo.something()


    # as decorator that derives the scope implicitly
    @graph.foo.scoped
    def myfunc(**kwargs):
         graph.foo.something()

    myfunc(scope="myscope")


**Note** that neither approach will work properly if the inner usage references
attributes of the proxies component that were captured outside of the scope setting.

That is, this idiom will **NOT** work:

    bar = graph.foo.bar

    with graph.foo.scoped_to("myscope"):
        # bar is not a proxy...
        bar.something()

"""
from contextlib import contextmanager
from functools import wraps


class ScopedProxy:
    """
    Proxy component requests back to the factory to dynamically resolve scope.

    Only proxies the attribute access and callables.

    """
    __slots__ = (
        "__graph__",
        "__factory__",
    )

    def __init__(self, graph, factory):
        self.__graph__ = graph
        self.__factory__ = factory

    @property
    def __component__(self):
        return self.__factory__.resolve(self.__graph__)

    def __call__(self, *args, **kwargs):
        return self.__component__(*args, **kwargs)

    def __getattr__(self, attr):
        return getattr(self.__component__, attr)

    @contextmanager
    def scoped_to(self, scope):
        """
        Context manager to switch scopes.

        """
        previous_scope = self.__factory__.current_scope
        try:
            self.__factory__.current_scope = scope
            yield
        finally:
            self.__factory__.current_scope = previous_scope

    def scoped(self, func):
        """
        Decorator to switch scopes.

        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            scope = kwargs.get("scope", self.__factory__.default_scope)
            with self.scoped_to(scope):
                return func(*args, **kwargs)
        return wrapper
