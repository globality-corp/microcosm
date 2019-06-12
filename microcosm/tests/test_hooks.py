"""
Test hook invocation.

"""
from hamcrest import assert_that, contains

from microcosm.api import binding, create_object_graph
from microcosm.hooks import on_resolve


def foo_hook(foo, value):
    foo.callbacks.append(value)


@binding("foo")
class Foo:

    def __init__(self, graph):
        self.callbacks = []


@binding("bar")
def new_foo(graph):
    return Foo(graph)


on_resolve(Foo, foo_hook, "baz")


class TestHooks:
    """
    Test hook invocations.

    """
    def test_on_resolve_foo_once(self):
        """
        Resolving Foo calls the hook.

        """
        graph = create_object_graph("test")
        graph.use("foo")
        graph.lock()

        assert_that(graph.foo.callbacks, contains("baz"))

    def test_on_resolve_foo_again(self):
        """
        Resolving Foo again results in only one hook call.

        """
        graph = create_object_graph("test")
        graph.use("foo")
        graph.lock()

        assert_that(graph.foo.callbacks, contains("baz"))

    def test_on_resolve_bar_once(self):
        """
        Resolving Foo through a separate factory calls the hook.

        """
        graph = create_object_graph("test")
        graph.use("bar")
        graph.lock()

        assert_that(graph.bar.callbacks, contains("baz"))

    def test_on_resolve_bar_again(self):
        """
        Resolving Foo through a separate factory again results in only one hook call.

        """
        graph = create_object_graph("test")
        graph.use("bar")
        graph.lock()

        assert_that(graph.bar.callbacks, contains("baz"))
