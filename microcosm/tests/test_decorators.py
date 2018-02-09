"""Tests for factory decorators"""
from hamcrest import (
    assert_that,
    contains,
    equal_to,
    has_entries,
    is_,
)

from microcosm.decorators import (
    binding,
    get_defaults,
    defaults,
    public,
)
from microcosm.loaders import load_each, load_from_dict
from microcosm.metadata import Metadata
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


def test_secure_and_insecure_config():
    metadata = Metadata("test")

    loader = load_each(
        public(
            load_from_dict(
                credentials=dict(
                    username="default",
                ),
            ),
        ),
        load_from_dict(
            credentials=dict(
                password="secret",
            ),
        ),
    )

    data = loader(metadata)

    assert_that(
        data,
        has_entries(
            credentials=dict(
                username="default",
                password="secret",
            ),
        ),
    )

    assert_that(
        metadata.keys["public"],
        contains("credentials.username"),
    )
