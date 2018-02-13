"""
Tests for configuration

"""
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    has_entry,
    has_property,
    instance_of,
    is_,
    raises,
)

from microcosm.config.model import Configuration


def test_attribute_access():
    """
    Configuration can be accessed by attribute and key.

    """
    config = Configuration(
        key="value",
        nested=dict(
            nested_key="nested_value",
            other_key=range(10),
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


def test_dont_merge():
    """
    Configuration support disabling recursive merging

    """
    config = Configuration(
        nested=dict(
            __merge__=False,
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
    assert_that(
        calling(getattr).with_args(config.nested, "nested_key"),
        raises(AttributeError),
    )
    assert_that(config.nested.other_key, is_(equal_to("new_value")))


def test_merge_lists():
    """
    Configuration merges lists but not tuples.

    """
    config = Configuration(
        lst1=[1, 2],
        lst2=[1, 2],
        tpl1=(1, 2),
        tpl2=(1, 2),
    )
    config.merge(
        lst1=[3, 4],
        lst2=(3, 4),
        tpl1=(3, 4),
        tpl2=[3, 4],
    )
    assert_that(config["lst1"], is_(equal_to([1, 2, 3, 4])))
    assert_that(config["lst2"], is_(equal_to((3, 4))))
    assert_that(config["tpl1"], is_(equal_to((3, 4))))
    assert_that(config["tpl2"], is_(equal_to([3, 4])))
