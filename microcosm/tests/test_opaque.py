"""
Opaque context tests.

"""
from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
    is_,
)

from microcosm.api import binding, create_object_graph, load_from_dict
from microcosm.opaque import NormalizedDict, Opaque


THIS = "this"
THAT = "that"
VALUE = "foo"
OTHER = "bar"
ALSO = "baz"


def example_func(this, that):
    return {
        THIS: this,
        THAT: that,
    }


def test_normalized_dict_init():
    dct = NormalizedDict()
    assert not dct

    dct = NormalizedDict(foo="bar", Bar="Foo", baz="qux")
    assert dct == {"foo": "bar", "bar": "Foo", "baz": "qux"}

    dct = NormalizedDict([("foo-foo", "bar"), ("Bar_Bar", "Foo"), ("baz", "qux")])
    assert dct == {"foo-foo": "bar", "bar_bar": "Foo", "baz": "qux"}

    dct = NormalizedDict({"foo-foo": "bar", "Bar_Bar": "Foo", "baz": "qux"})
    assert dct == {"foo-foo": "bar", "bar_bar": "Foo", "baz": "qux"}

    dct = NormalizedDict.fromkeys(["foo", "bar"], 1)
    assert dct == {"foo": 1, "bar": 1}


def test_normalized_dict_setitem():
    dct = NormalizedDict()
    dct["FOO"] = "Bar"
    assert dct["foo"] == "Bar"
    assert dct.get("foo") == "Bar"

    dct[(1, 1)] = "foo"
    assert dct[(1, 1)] == "foo"


def test_normalized_dict_getitem():
    dct = NormalizedDict()
    dct["foo"] = "bar"
    assert dct["FOO"] == "bar"


def test_normalized_dict_delitem():
    dct = NormalizedDict()
    dct["foo"] = "bar"
    del dct["FOO"]
    assert not dct
    assert dct.get("foo") is None


def test_normalized_dict_contains():
    dct = NormalizedDict()
    dct["foo"] = "bar"
    assert "FOO" in dct
    assert "bar" not in dct


def test_normalized_dict_pop():
    dct = NormalizedDict()
    dct["foo"] = "bar"
    assert dct.pop("FOO") == "bar"
    assert not dct
    assert dct.pop("bar", "baz") == "baz"


def test_normalized_dict_get():
    dct = NormalizedDict()
    dct["foo"] = "bar"
    assert dct.get("FOO") == "bar"
    assert dct.get("FOO", "baz") == "bar"
    assert dct.get("baz", "bar") == "bar"


def test_normalized_dict_update():
    dct = NormalizedDict()
    dct["foo"] = "Bar"
    dct.update({"FOO": "Baz", "bar": "Foo"})
    assert dct == {"foo": "Baz", "bar": "Foo"}


def test_normalized_dict_setdefault():
    dct = NormalizedDict()
    dct.setdefault("Foo", "bar")
    assert dct["foo"] == "bar"


def test_dict_usage():
    """
    Opaque should be dict-like.

    """
    opaque = Opaque()
    assert_that(opaque.as_dict(), is_(equal_to(dict())))

    opaque[THIS] = VALUE
    assert_that(opaque.as_dict(), is_(equal_to({THIS: VALUE})))
    assert_that(opaque[THIS], is_(equal_to(VALUE)))


def test_context_manager():
    """
    Opaque.initialize should act as a context manager and resets state properly.

    """
    opaque = Opaque()

    opaque[THIS] = VALUE
    assert_that(opaque.as_dict(), is_(equal_to({THIS: VALUE})))

    with opaque.initialize(example_func, OTHER, OTHER):
        assert_that(opaque.as_dict(), is_(equal_to(example_func(OTHER, OTHER))))
        assert_that(opaque.as_dict(), is_(equal_to({THIS: OTHER, THAT: OTHER})))

    with opaque.initialize(example_func, OTHER, OTHER):
        assert_that(opaque.as_dict(), is_(equal_to(example_func(OTHER, OTHER))))
        assert_that(opaque.as_dict(), is_(equal_to({THIS: OTHER, THAT: OTHER})))

    assert_that(opaque.as_dict(), is_(equal_to({THIS: VALUE})))


def test_decorator():
    """
    Opaque.initialize should act as a decorator and resets state properly.

    """
    opaque = Opaque()
    opaque[THIS] = VALUE

    @opaque.initialize(example_func, OTHER, OTHER)
    def function_to_decorate():
        return opaque.as_dict()

    assert_that(opaque.as_dict(), is_(equal_to({THIS: VALUE})))
    assert_that(function_to_decorate(), is_(equal_to(example_func(OTHER, OTHER))))
    assert_that(opaque.as_dict(), is_(equal_to({THIS: VALUE})))
    assert_that(function_to_decorate(), is_(equal_to(example_func(OTHER, OTHER))))
    assert_that(opaque.as_dict(), is_(equal_to({THIS: VALUE})))


def test_composition():
    """
    Opaque.initialize should compose (within reason).

    """
    opaque = Opaque()
    opaque[THIS] = VALUE

    assert_that(opaque.as_dict(), is_(equal_to({THIS: VALUE})))
    with opaque.initialize(example_func, OTHER, OTHER):
        assert_that(opaque.as_dict(), is_(equal_to(example_func(OTHER, OTHER))))
        with opaque.initialize(example_func, ALSO, OTHER):
            assert_that(opaque.as_dict(), is_(equal_to(example_func(ALSO, OTHER))))
        assert_that(opaque.as_dict(), is_(equal_to(example_func(OTHER, OTHER))))
    assert_that(opaque.as_dict(), is_(equal_to({THIS: VALUE})))


# set up a parent collaborator that uses a child collaborator
@binding("parent_collaborator")
class Parent:
    def __init__(self, graph):
        self.child_collaborator = graph.child_collaborator

    def __call__(self):
        return self.child_collaborator()


@binding("child_collaborator")
class Child:
    def __init__(self, graph):
        self.opaque = graph.opaque

    def __call__(self):
        return self.opaque.as_dict()


def test_collaboration():
    """
    All microcosm collaborators should have access to the same opaque context.

    """
    # create the object graph with both collaborators and opaque data
    graph = create_object_graph(
        "test",
        testing=True,
        loader=load_from_dict(
            opaque={THIS: VALUE},
            tracer={"enabled": True},
        )
    )

    graph.use(
        "child_collaborator",
        "opaque",
        "parent_collaborator",
    )
    graph.lock()

    # we should be able to initialize the opaque data and observe it from the collaborators
    decorated_func = graph.opaque.initialize(
        example_func, OTHER, OTHER
    )(graph.parent_collaborator.__call__)

    assert_that(graph.opaque.as_dict(), is_(equal_to({THIS: VALUE})))
    # NB: opaque.initialize will also inject some jaeger-related metadata which the tests can ignore.
    assert_that(decorated_func(), has_entries(example_func(OTHER, OTHER)))
    assert_that(graph.opaque.as_dict(), is_(equal_to({THIS: VALUE})))
