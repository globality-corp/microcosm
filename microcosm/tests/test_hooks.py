"""
Test hook invocation.

"""
from hamcrest import assert_that, contains_exactly
from nose.tools import assert_raises_regexp

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
        assert_that(graph.clazz.callbacks, contains_exactly("clazz_resolved"))

    def test_on_resolve_clazz_again(self):
        """
        Resolving Clazz twice results in only one hook call, because the object is not created twice.

        """
        graph = create_object_graph("test")
        graph.use("clazz")
        assert_that(graph.clazz.callbacks, contains_exactly("clazz_resolved"))
        graph.use("clazz")
        assert_that(graph.clazz.callbacks, contains_exactly("clazz_resolved"))

    def test_on_resolve_clazz_subclazz(self):
        """
        If we have two components, and one is a subclass of the other's class, we should
        still have isolation of the hooks between them

        """
        graph = create_object_graph("test")
        graph.use("clazz")
        graph.use("subclazz")

        assert_that(graph.clazz.callbacks, contains_exactly("clazz_resolved"))
        assert_that(graph.subclazz.callbacks, contains_exactly("subclazz_resolved"))

    def test_on_resolve_clazz2_once(self):
        """
        Resolving Clazz through a separate factory calls the hook.

        """
        graph = create_object_graph("test")
        graph.use("clazz")
        graph.use("clazz2")

        assert graph.clazz is not graph.clazz2
        assert_that(graph.clazz.callbacks, contains_exactly("clazz_resolved"))
        assert_that(graph.clazz2.callbacks, contains_exactly("clazz_resolved"))

    def test_on_resolve_clazz2_again(self):
        """
        Resolving Clazz through a separate factory again results in only one hook call.

        """
        graph = create_object_graph("test")
        graph.use("clazz2")
        assert_that(graph.clazz2.callbacks, contains_exactly("clazz_resolved"))
        graph.use("clazz2")
        assert_that(graph.clazz2.callbacks, contains_exactly("clazz_resolved"))

    def test_no_hooks(self):
        @binding("clazz_no_hooks")
        class ClazzNoHooks(Clazz):
            pass
        graph = create_object_graph("test")
        graph.use("clazz_no_hooks")
        assert_that(graph.clazz_no_hooks.callbacks == [])

    def test_hook_type_error_does_not_stop_subsequent_hooks(self):
        @binding("clazz_type_error")
        class ClazzTypeError(Clazz):
            pass

        def throw_type_error(any_object, value):
            raise TypeError()
        on_resolve(ClazzTypeError, throw_type_error, "string")
        on_resolve(ClazzTypeError, append_callbacks, "hook2")

        graph = create_object_graph("test")
        graph.use("clazz_type_error")
        assert_that(graph.clazz_type_error.callbacks, contains_exactly("hook2"))

    def test_hook_value_error_does_not_stop_subsequent_hooks(self):
        @binding("clazz_value_error")
        class ClazzValueError(Clazz):
            pass

        def throw_value_error(any_object, value):
            raise ValueError()
        on_resolve(ClazzValueError, throw_value_error, "string")
        on_resolve(ClazzValueError, append_callbacks, "hook2")

        graph = create_object_graph("test")
        graph.use("clazz_value_error")
        assert_that(graph.clazz_value_error.callbacks, contains_exactly("hook2"))

    def test_hook_error_getting_hooks(self):
        @binding("clazz_exception")
        class ClazzException(Clazz):
            def __getattr__(self, name):
                raise Exception("my message")

        graph = create_object_graph("test")
        with assert_raises_regexp(Exception, "my message"):
            graph.use("clazz_exception")
