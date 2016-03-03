"""Registry tests"""
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    is_,
    not_none,
    raises,
)

from microcosm.errors import AlreadyBoundError, NotBoundError
from microcosm.registry import Registry


def create_foo(*args, **kwargs):
    return "foo"


def create_bar(*args, **kwargs):
    return "bar"


def test_bind_and_resolve():
    """
    Binding a function allows it be resolved.

    """
    registry = Registry()
    registry.bind("foo", create_foo)
    factory = registry.resolve("foo")
    assert_that(factory, is_(equal_to(create_foo)))


def test_resolve_entry_point():
    """
    Resolving an entry point function works without binding.

    """
    registry = Registry()
    factory = registry.resolve("hello_world")
    assert_that(factory, is_(not_none()))


def test_bind_duplicate():
    """
    Binding to the same key multiple times raises an error.

    """
    registry = Registry()
    registry.bind("foo", create_foo)
    assert_that(
        calling(registry.bind).with_args("foo", create_bar),
        raises(AlreadyBoundError),
    )


def test_resolve_not_found():
    """
    Resolving an unbound function raises an error.

    """
    registry = Registry()
    assert_that(
        calling(registry.resolve).with_args("foo"),
        raises(NotBoundError),
    )
