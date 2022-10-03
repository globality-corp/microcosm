"""
Object Graph Tests

"""
from unittest.mock import Mock

from hamcrest import (
    assert_that,
    calling,
    contains,
    equal_to,
    has_items,
    instance_of,
    is_,
    raises,
)

from microcosm.api import get_component_name
from microcosm.decorators import binding, defaults
from microcosm.errors import CyclicGraphError, LockedGraphError
from microcosm.object_graph import create_object_graph
from microcosm.registry import Registry


class Parent:
    def __init__(self, child):
        self.child = child


# bind with a function
@binding("parent")
def create_parent(graph):
    return Parent(graph.child)


# bind with a constructor
@binding("child")
@defaults(value="default_value")
class Child:
    def __init__(self, graph):
        self.value = graph.config.child.value


def test_create_object_graph():
    """
    Construct an object graph from bound factories and entry points.

    """
    graph = create_object_graph(
        name="test",
    )
    assert_that(graph.child, is_(instance_of(Child)))
    assert_that(graph.child.value, is_(equal_to("default_value")))
    assert_that(graph.parent, is_(instance_of(Parent)))
    assert_that(graph.parent.child, is_(equal_to(graph.child)))
    assert_that(graph.hello_world, is_(equal_to("hello world")))


def test_object_graph_use():
    """
    Explicitly create a set of components.

    """
    graph = create_object_graph(
        name="test",
    )
    parent, _ = graph.use("parent", "hello_world")
    assert_that(graph.get("parent"), is_(instance_of(Parent)))
    assert_that(parent, is_(instance_of(Parent)))
    assert_that(
        list(graph.items()),
        has_items(
            contains("parent", is_(instance_of(Parent))),
            contains("child", is_(instance_of(Child))),
            contains("hello_world", is_(equal_to("hello world"))),
        )
    )


def test_object_graph_partial_use():
    """
    Partial initialization succeeds partially and is recoverable.

    """
    registry = Registry()

    create_first = Mock()
    create_first.return_value = "first"
    create_second = Mock()
    create_second.side_effect = [Exception, "second"]
    create_third = Mock()
    create_third.side_effect = "third"

    registry.bind("first", create_first)
    registry.bind("second", create_second)
    registry.bind("third", create_third)

    graph = create_object_graph("test", registry=registry)
    # exception raised from initial call to create_second
    assert_that(
        calling(graph.use).with_args("first", "second", "third"), raises(Exception)
    )
    # first and second were called, but not third
    assert_that(create_first.call_count, is_(equal_to(1)))
    assert_that(create_second.call_count, is_(equal_to(1)))
    assert_that(create_third.call_count, is_(equal_to(0)))

    # second call succeeds
    [first, second, third] = graph.use("first", "second", "third")
    # first was not called, second was called again, and third called for the first time
    assert_that(create_first.call_count, is_(equal_to(1)))
    assert_that(create_second.call_count, is_(equal_to(2)))
    assert_that(create_third.call_count, is_(equal_to(1)))


def test_object_graph_locking():
    """
    Locking and unlocking a graph effects its ability to create components.

    """
    graph = create_object_graph(
        name="test",
    )
    [parent] = graph.use("parent")
    graph.lock()

    # can access already created object
    assert_that(graph.parent, is_(equal_to(parent)))
    # cannot create a new object
    assert_that(calling(graph.use).with_args("hello_world"), raises(LockedGraphError))

    graph.unlock()

    # can create an object again
    [hello_world] = graph.use("hello_world")
    assert_that(hello_world, is_(equal_to("hello world")))


def test_object_graph_cycle():
    """
    Graph cycles are detected.

    """
    registry = Registry()

    @binding("cycle", registry=registry)
    def create_cycle(graph):
        return graph.cycle

    graph = create_object_graph("test", registry=registry)
    assert_that(calling(graph.use).with_args("cycle"), raises(CyclicGraphError))


def test_get_component_name_function():
    """
    Utility function `get_component_name` works.

    """
    graph = create_object_graph(
        name="test",
    )
    graph.use("parent")
    graph.lock()

    assert_that(get_component_name(graph, graph.parent), is_(equal_to("parent")))


def test_describe_object_graph():
    graph = create_object_graph(
        name="test", description="A description of the object graph."
    )
    assert_that(
        graph.metadata.description, is_(equal_to("A description of the object graph."))
    )


def test_default_object_graph_description():
    graph = create_object_graph(
        name="test",
    )
    assert_that(graph.metadata.description, is_(equal_to("")))
