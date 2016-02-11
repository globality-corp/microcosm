"""Registry tests"""
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    is_,
    raises,
)

from marquez.errors import AlreadyBoundError, NotBoundError
from marquez.registry import Registry


def create_foo(*args, **kwargs):
    return "foo"


def create_bar(*args, **kwargs):
    return "bar"


def test_register_and_resolve():
    registry = Registry()
    registry.register("foo", create_foo)
    factory = registry.resolve("foo")
    assert_that(factory, is_(equal_to(create_foo)))


def test_register_duplicate():
    registry = Registry()
    registry.register("foo", create_foo)
    assert_that(
        calling(registry.register).with_args("foo", create_bar),
        raises(AlreadyBoundError),
    )


def test_resolve_not_found():
    registry = Registry()
    assert_that(
        calling(registry.resolve).with_args("foo"),
        raises(NotBoundError),
    )
