"""Tests for factory decorators"""
from hamcrest import (
    assert_that,
    equal_to,
    is_,
)

from microcosm.decorators import (
    binding,
    defaults,
    get_defaults,
)
from microcosm.registry import Registry


def test_defaults():
    """
    Defaults can be set and retrieved.

    """
    @defaults(foo="bar")
    def func(*args, **kwargs):
        pass

    assert_that(get_defaults(func), is_(equal_to(dict(foo="bar"))))


def test_defaults_not_set():
    """
    Defaults default to an empty dict.

    """
    def func(*args, **kwargs):
        pass

    assert_that(get_defaults(func), is_(equal_to(dict())))


def test_binding():
    """
    Binding registers function.

    """
    registry = Registry()

    @binding("foo", registry=registry)
    def func(*args, **kwargs):
        pass

    assert_that(registry.resolve("foo"), is_(equal_to(func)))
