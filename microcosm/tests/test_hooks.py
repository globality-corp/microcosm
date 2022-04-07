"""
Test hook invocation.

"""
from hamcrest import assert_that, contains_exactly

from microcosm.api import binding, create_object_graph
from microcosm.hooks import on_resolve


def append_callbacks(any_object, value):
    any_object.callbacks.append(value)


@binding("clazz")
class Clazz:
    def __init__(self, graph):
        self.callbacks = []


@binding("subclazz")
class SubClazz(Clazz):
    pass


@binding("clazz2")
def new_clazz(graph):
    return Clazz(graph)


on_resolve(Clazz, append_callbacks, "clazz_resolved")
on_resolve(SubClazz, append_callbacks, "subclazz_resolved")


class TestHooks:
    """
    Test hook invocations.

    """
    def test_on_resolve_clazz_once(self):
        """
        Resolving Clazz calls the hook.

        """
        graph = create_object_graph("test")
        graph.use("clazz")
        graph.lock()

        assert_that(graph.clazz.callbacks, contains_exactly("clazz_resolved"))

    def test_on_resolve_clazz_again(self):
        """
        Resolving Clazz again results in only one hook call.

        """
        graph = create_object_graph("test")
        graph.use("clazz")
        graph.lock()

        assert_that(graph.clazz.callbacks, contains_exactly("clazz_resolved"))

    def test_on_resolve_clazz_subclazz(self):
        """
        If we have two components, and one is a subclass of the other's class, we should
        still have isolation of the hooks between them

        """
        graph = create_object_graph("test")
        graph.use("clazz")
        graph.use("subclazz")
        graph.lock()

        assert_that(graph.clazz.callbacks, contains_exactly("clazz_resolved"))
        assert_that(graph.subclazz.callbacks, contains_exactly("subclazz_resolved"))

    def test_on_resolve_clazz2_once(self):
        """
        Resolving Clazz through a separate factory calls the hook.

        """
        graph = create_object_graph("test")
        graph.use("clazz2")
        graph.lock()

        assert_that(graph.clazz2.callbacks, contains_exactly("clazz_resolved"))

    def test_on_resolve_clazz2_again(self):
        """
        Resolving Clazz through a separate factory again results in only one hook call.

        """
        graph = create_object_graph("test")
        graph.use("clazz2")
        graph.lock()

        assert_that(graph.clazz2.callbacks, contains_exactly("clazz_resolved"))
