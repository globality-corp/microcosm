"""
Test hook invocation.

"""
from hamcrest import assert_that, contains_exactly

from microcosm.api import binding, create_object_graph
from microcosm.hooks import on_resolve


def foo_hook(foo, value):
    foo.callbacks.append(value)


@binding("foo")
class Foo:

    def __init__(self, graph):
        self.callbacks = []


@binding("subfoo")
class SubFoo(Foo):
    pass


@binding("bar")
def new_foo(graph):
    return Foo(graph)


on_resolve(Foo, foo_hook, "baz")
on_resolve(SubFoo, foo_hook, "qux")


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

        assert_that(graph.foo.callbacks, contains_exactly("baz"))

    def test_on_resolve_foo_again(self):
        """
        Resolving Foo again results in only one hook call.

        """
        graph = create_object_graph("test")
        graph.use("foo")
        graph.lock()

        assert_that(graph.foo.callbacks, contains_exactly("baz"))

    def test_on_resolve_foo_subfoo(self):
        """
        If we have two components, and one is a subclass of the other's class, we should
        still have isolation of the hooks between them

        """
        graph = create_object_graph("test")
        graph.use("foo")
        graph.use("subfoo")
        graph.lock()

        assert_that(graph.foo.callbacks, contains_exactly("baz"))
        assert_that(graph.subfoo.callbacks, contains_exactly("qux"))

    def test_on_resolve_bar_once(self):
        """
        Resolving Foo through a separate factory calls the hook.

        """
        graph = create_object_graph("test")
        graph.use("bar")
        graph.lock()

        assert_that(graph.bar.callbacks, contains_exactly("baz"))

    def test_on_resolve_bar_again(self):
        """
        Resolving Foo through a separate factory again results in only one hook call.

        """
        graph = create_object_graph("test")
        graph.use("bar")
        graph.lock()

        assert_that(graph.bar.callbacks, contains_exactly("baz"))
