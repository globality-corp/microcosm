"""Module loading tests"""
from hamcrest import (
    assert_that,
    equal_to,
    is_,
)

from microcosm.object_graph import create_object_graph


def test_importing():
    """
    Importing can be used to access object graph members.

    """
    graph = create_object_graph(
        name="test",
    )
    graph.use("hello_world")
    graph.export("some.module")
    from some.module import hello_world
    assert_that(hello_world, is_(equal_to("hello world")))
