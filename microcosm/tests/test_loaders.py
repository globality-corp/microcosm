"""Configuration loading tests"""
from contextlib import contextmanager
from json import dumps
from os import environ
from tempfile import NamedTemporaryFile

from hamcrest import (
    assert_that,
    empty,
    equal_to,
    is_,
    none,
)

from microcosm.loaders import (
    expand_config,
    get_config_filename,
    load_each,
    load_from_environ,
    load_from_environ_as_json,
    load_from_json_file,
    load_from_python_file,
)
from microcosm.metadata import Metadata


@contextmanager
def envvar(key, value):
    """
    Temporarily set an environment variable.

    """
    old_value = environ.get(key)
    environ[key] = value
    yield
    if old_value is None:
        del environ[key]
    else:
        environ[key] = value


@contextmanager
def configfile(data):
    """
    Temporarily create a temporary file.

    """
    configfile_ = NamedTemporaryFile(mode='w+')
    configfile_.write(data)
    configfile_.flush()
    yield configfile_


def test_expand_config():
    """
    Configuration expansion should work.

    """
    assert_that(
        expand_config(
            {
                "prefix.foo": "bar",
                "prefix.BAR.baz": lambda: "foo",
                "this": "that",
            },
            key_parts_filter=lambda key_parts: key_parts[0] == "prefix",
            skip_to=1,
        ),
        is_(equal_to(
            {
                "foo": "bar",
                "bar": {
                    "baz": "foo",
                },
            },
        )),
    )


def test_get_config_filename_not_set():
    """
    If the envvar is not set, not filename is returned.

    """
    metadata = Metadata("foo-bar")
    config_filename = get_config_filename(metadata)
    assert_that(config_filename, is_(none()))


def test_get_config_filename():
    """
    If the envvar is set, it is used as the filename.

    """
    metadata = Metadata("foo-bar")
    with envvar("FOO_BAR_SETTINGS", "/tmp/foo-bar.conf"):
        config_filename = get_config_filename(metadata)
        assert_that(config_filename, is_(equal_to("/tmp/foo-bar.conf")))


def test_load_from_json_file():
    """
    Return configuration from a json file.

    """
    metadata = Metadata("foo-bar")
    with configfile(dumps(dict(foo="bar"))) as configfile_:
        with envvar("FOO_BAR_SETTINGS", configfile_.name):
            config = load_from_json_file(metadata)
            assert_that(config.foo, is_(equal_to("bar")))


def test_load_from_json_file_not_set():
    """
    Return empty configuration if json file is not defined.

    """
    metadata = Metadata("foo-bar")
    config = load_from_json_file(metadata)
    assert_that(config, is_(empty()))


def test_load_from_python_file():
    """
    Return configuration from a python file.

    """
    metadata = Metadata("foo-bar")
    with configfile("foo='bar'") as configfile_:
        with envvar("FOO_BAR_SETTINGS", configfile_.name):
            config = load_from_python_file(metadata)
            assert_that(config.foo, is_(equal_to("bar")))


def test_load_from_python_file_not_set():
    """
    Return empty configuration if python file is not defined.

    """
    metadata = Metadata("foo-bar")
    config = load_from_python_file(metadata)
    assert_that(config, is_(empty()))


def test_load_from_environ():
    """
    Return configuration from environment.

    """
    metadata = Metadata("foo")
    with envvar("FOO_BAR", "baz"):
        with envvar("FOO_FOO_THIS", "that"):
            config = load_from_environ(metadata)
    assert_that(config, is_(equal_to({"bar": "baz", "foo": {"this": "that"}})))


def test_load_from_environ_double_underscore():
    """
    Return configuration from environment.

    """
    metadata = Metadata("foo")
    with envvar("FOO_BAR", "baz"):
        with envvar("FOO__BAZ", "bar"):
            with envvar("FOO__BAR_BAZ__THIS", "that"):
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
    with envvar("FOO_BAR", "baz"):
        with envvar("FOO_FOO_THIS", "that"):
            with envvar("FOO_FOO_THAT", "this"):
                config = load_from_environ(metadata)
    assert_that(config, is_(equal_to({"bar": "baz", "foo": {"this": "that", "that": "this"}})))


def test_load_from_environ_json():
    """
    Return json configuration from environment.

    """
    metadata = Metadata("foo")
    with envvar("FOO_BAR", '["baz"]'):
        with envvar("FOO_BAZ", 'true'):
            config = load_from_environ_as_json(metadata)
    assert_that(config, is_(equal_to({"bar": ["baz"], "baz": True})))


def test_load_from_environ_multipart_name():
    """
    Return configuration from environment.

    """
    metadata = Metadata("foo-bar")
    with envvar("FOO_BAR_BAZ", "blah"):
        config = load_from_environ(metadata)
    assert_that(config, is_(equal_to({"baz": "blah"})))


def test_load_each():
    """
    Return the merged union of two loaders.

    """
    metadata = Metadata("foo")
    with configfile(dumps(dict(foo="bar"))) as configfile_:
        with envvar("FOO_SETTINGS", configfile_.name):
            with envvar("FOO_BAR", "baz"):
                loader = load_each(load_from_json_file, load_from_environ)
                config = loader(metadata)
    assert_that(config, is_(equal_to({
        "bar": "baz",
        "foo": "bar",
        "settings": configfile_.name
    })))
