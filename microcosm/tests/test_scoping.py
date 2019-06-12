"""
Test binding scoping.

"""
from hamcrest import (
    assert_that,
    equal_to,
    instance_of,
    is_,
)

from microcosm.api import create_object_graph, defaults, load_from_dict
from microcosm.scoping import ScopedFactory, scoped_binding


@scoped_binding("adder")
@defaults(
    first=1,
    second=2,
)
class Adder:

    def __init__(self, graph):
        self.first = graph.config.adder.first
        self.second = graph.config.adder.second

    def __call__(self):
        return self.first + self.second


@scoped_binding("counter")
class Counter:
    count = 0

    def __init__(self, graph):
        Counter.count += 1
        self.count = Counter.count


def test_binding():
    """
    Binding functionality works as usual.

    """
    graph = create_object_graph("example", testing=True)
    assert_that(graph.adder(), is_(equal_to(3)))


def test_scoped_to():
    """
    Factory can be scoped to a specific value.

    """
    loader = load_from_dict(
        bar=dict(
            adder=dict(
                first=3,
            ),
        ),
    )
    graph = create_object_graph("example", testing=True, loader=loader)

    with graph.adder.scoped_to("bar"):
        assert_that(graph.adder(), is_(equal_to(5)))

    with graph.adder.scoped_to("baz"):
        assert_that(graph.adder(), is_(equal_to(3)))


def test_scoped():
    loader = load_from_dict(
        bar=dict(
            adder=dict(
                first=3,
            ),
        ),
    )
    graph = create_object_graph("example", testing=True, loader=loader)

    @graph.adder.scoped
    def helper(expected, **kwargs):
        assert_that(graph.adder(), is_(equal_to(expected)))

    helper(3)
    helper(5, scope="bar")
    helper(3, scope="baz")


def test_infect_entry_point():
    """
    Entry points can be converted to ScopedFactories after-the-fact.

    """
    graph = create_object_graph("example", testing=True)
    ScopedFactory.infect(graph, "hello_world")

    factory = graph._registry.resolve("hello_world")
    assert_that(factory, is_(instance_of(ScopedFactory)))


def test_caching():
    """
    Caching works (within the scoped factory)

    """
    graph = create_object_graph("example", testing=True)
    assert_that(Counter.count, is_(equal_to(0)))
    assert_that(graph.counter.count, is_(equal_to(1)))
    assert_that(graph.counter.count, is_(equal_to(1)))
    assert_that(Counter.count, is_(equal_to(1)))
