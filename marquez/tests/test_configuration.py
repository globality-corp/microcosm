"""Tests for configuration"""
from hamcrest import (
    assert_that,
    equal_to,
    has_entry,
    has_property,
    instance_of,
    is_,
)

from marquez.configuration import Configuration


def test_attribute_access():
    """
    Configuration can be accessed by attribute and key.

    """
    config = Configuration(
        key="value",
        nested=dict(
            nested_key="nested_value",
        )
    )
    assert_that(config, has_entry("key", "value"))
    assert_that(config, has_property("key", "value"))
    assert_that(config["nested"], is_(instance_of(Configuration)))
    assert_that(config["nested"], has_entry("nested_key", "nested_value"))
    assert_that(config.nested, has_property("nested_key", "nested_value"))


def test_merge():
    """
    Configuration support recursive merging

    """
    config = Configuration(
        nested=dict(
            nested_key="nested_value",
            other_key="initial_value",
        )
    )
    config.merge(
        key="value",
        nested=dict(
            other_key="new_value",
        ),
    )
    assert_that(config.key, is_(equal_to("value")))
    assert_that(config.nested.nested_key, is_(equal_to("nested_value")))
    assert_that(config.nested.other_key, is_(equal_to("new_value")))

    config.merge(
        dict(key=dict()),
    )
    assert_that(config.key, is_(equal_to(dict())))
