"""Object Graph Tests"""
from hamcrest import (
    assert_that,
    equal_to,
    instance_of,
    is_,
)

from marquez.decorators import defaults, binding
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
