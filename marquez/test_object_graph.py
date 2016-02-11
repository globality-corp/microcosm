"""Object Graph Tests"""
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    instance_of,
    is_,
    raises,
)

from marquez.decorators import defaults, binding
from marquez.errors import LockedGraphError
from marquez.object_graph import create_object_graph


class Parent(object):
    def __init__(self, child):
        self.child = child


# bind with a function
@binding("parent")
def create_parent(graph):
    return Parent(graph.child)


# bind with a constructor
@binding("child")
@defaults(value="default_value")
class Child(object):
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
    parent, _ = graph.use(
        "parent",
        "hello_world"
    )
    assert_that(parent, is_(instance_of(Parent)))


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
