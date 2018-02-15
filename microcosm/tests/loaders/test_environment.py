from hamcrest import assert_that, equal_to, is_

from microcosm.loaders import load_from_environ, load_from_environ_as_json
from microcosm.metadata import Metadata
from microcosm.tests.loaders.fixtures import envvar


def test_load_from_environ():
    """
    Return configuration from environment.

    """
    metadata = Metadata("foo-dow")
    with envvar("FOO_DOW__BAR", "baz"):
        with envvar("FOO_DOW__BAZ", "bar"):
            with envvar("FOO_DOW__BAR_BAZ__THIS", "that"):
                config = load_from_environ(metadata)
    assert_that(config, is_(equal_to({
        "bar": "baz",
        "baz": "bar",
        "bar_baz": {"this": "that"}}
    )))


def test_load_multiple_values_for_on_componentfrom_environ():
    """
    Return configuration from environment.

    """
    metadata = Metadata("foo")
    with envvar("FOO__BAR", "baz"):
        with envvar("FOO__FOO__THIS", "that"):
            with envvar("FOO__FOO__THAT", "this"):
                config = load_from_environ(metadata)
    assert_that(config, is_(equal_to({"bar": "baz", "foo": {"this": "that", "that": "this"}})))


def test_load_from_environ_json():
    """
    Return json configuration from environment.

    """
    metadata = Metadata("foo")
    with envvar("FOO__BAR", '["baz"]'):
        with envvar("FOO__BAZ", 'true'):
            config = load_from_environ_as_json(metadata)
    assert_that(config, is_(equal_to({"bar": ["baz"], "baz": True})))


def test_load_from_environ_multipart_name():
    """
    Return configuration from environment.

    """
    metadata = Metadata("foo-bar")
    with envvar("FOO_BAR__BAZ", "blah"):
        config = load_from_environ(metadata)
    assert_that(config, is_(equal_to({"baz": "blah"})))
