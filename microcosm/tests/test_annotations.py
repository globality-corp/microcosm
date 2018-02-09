"""
Annotation tests.

"""
from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
    is_,
)

from microcosm.api import create_object_graph, binding, defaults
from microcosm.annotations import boolean, must_override, required, split
from microcosm.decorators import get_defaults
from microcosm.loaders import load_from_dict
from microcosm.registry import Registry


REGISTRY = Registry()


@binding("integer", REGISTRY)
@defaults(
    value=int,
)
def integer(graph):
    return graph.config.integer.value


@binding("boolean", REGISTRY)
@defaults(
    value=boolean,
)
def boolean(graph):
    return graph.config.boolean.value


@binding("component", REGISTRY)
@defaults(
    values=must_override,
    more=required,
)
def component(graph):
    return graph.config.component


def test_split_annotations():
    defaults = {
        key: get_defaults(value)
        for key, value in REGISTRY.all.items()
    }
    configuration, annotations = split(defaults)
    assert_that(
        configuration,
        has_entries(
            integer=dict(),
        ),
    )

    assert_that(
        annotations,
        has_entries(
            integer=has_entries(
                value=int,
            ),
        ),
    )


def test_annotated_config():
    loader = load_from_dict(
        boolean=dict(
            value="no",
        ),
        integer=dict(
            value="1",
        ),
        component=dict(
            values=[
                "one",
                "two",
            ],
            more=[
                "three",
                "four",
            ],
        ),
    )
    graph = create_object_graph("test", loader=loader, registry=REGISTRY)
    assert_that(graph.boolean, is_(equal_to(False)))
    assert_that(graph.component, is_(equal_to(dict(
        values=[
            "one",
            "two",
        ],
        more=[
            "three",
            "four",
        ],
    ))))
