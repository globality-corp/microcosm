"""
Test loading function composition.

"""
from json import dumps

from hamcrest import assert_that, equal_to, is_

from microcosm.config.model import Configuration
from microcosm.loaders import load_from_dict
from microcosm.loaders.compose import (
    load_config_and_secrets,
    load_each,
    load_partitioned,
    two_stage_loader,
)
from microcosm.loaders.environment import load_from_environ
from microcosm.loaders.settings import load_from_json_file
from microcosm.metadata import Metadata
from microcosm.tests.loaders.fixtures import envvar, settings


def test_load_each():
    """
    Return the merged union of two loaders.

    """
    metadata = Metadata("foo")
    with settings(dumps(dict(foo="bar"))) as settings_:
        with envvar("FOO__SETTINGS", settings_.name):
            with envvar("FOO__BAR", "baz"):
                loader = load_each(load_from_json_file, load_from_environ)
                config = loader(metadata)

    assert_that(config, is_(equal_to({
        "bar": "baz",
        "foo": "bar",
        "settings": settings_.name
    })))


def secondary_loader(metadata, config):
    return Configuration({
        config.foo: "bazman",
    })


def test_two_stage_loader_basic():
    metadata = Metadata("foo")
    initial_loader = load_from_dict(
        foo="bar",
    )

    loader = two_stage_loader(initial_loader, secondary_loader)
    config = loader(metadata)

    assert_that(config, is_(equal_to(dict(
        foo="bar",
        bar="bazman",
    ))))


def test_two_stage_loader_prefer_primary():
    metadata = Metadata("foo")
    initial_loader = load_from_dict(
        foo="bar",
        bar="hello",
    )

    loader = two_stage_loader(
        initial_loader,
        secondary_loader,
        prefer_secondary=False,
    )
    config = loader(metadata)

    assert_that(config, is_(equal_to(dict(
        foo="bar",
        bar="hello",
    ))))


def test_two_stage_loader_prefer_secondary():
    metadata = Metadata("foo")
    initial_loader = load_from_dict(
        foo="bar",
        bar="hello",
    )
    loader = two_stage_loader(
        initial_loader,
        secondary_loader,
        prefer_secondary=True,
    )
    config = loader(metadata)

    assert_that(config, is_(equal_to(dict(
        foo="bar",
        bar="bazman",
    ))))


def test_load_partitioned():
    metadata = Metadata("foo")
    loader = load_partitioned(
        foo=load_from_dict(
            foo=dict(
                value="foo",
            ),
            baz=dict(
                value="foo",
                foo=dict(
                    value="foo",
                ),
            ),
        ),
        bar=load_from_dict(
            bar=dict(
                value="bar",
            ),
            baz=dict(
                value="bar",
                bar=dict(
                    value="bar",
                ),
            ),
        ),
    )
    config = loader(metadata)

    # configuration is loaded as a usual merge
    assert_that(config, is_(equal_to(dict(
        foo=dict(
            value="foo",
        ),
        bar=dict(
            value="bar",
        ),
        baz=dict(
            value="bar",
            foo=dict(
                value="foo",
            ),
            bar=dict(
                value="bar",
            ),
        ),
    ))))

    # loader retains partitions
    assert_that(loader.foo, is_(equal_to(dict(
        foo=dict(
            value="foo",
        ),
        baz=dict(
            foo=dict(
                value="foo",
            ),
        ),
    ))))
    assert_that(loader.bar, is_(equal_to(dict(
        bar=dict(
            value="bar",
        ),
        baz=dict(
            value="bar",
            bar=dict(
                value="bar",
            ),
        ),
    ))))


def test_load_config_and_secrets():
    metadata = Metadata("foo")
    loader = load_config_and_secrets(
        config=load_from_dict(
            credentials=dict(
                username="default",
            ),
        ),
        secrets=load_from_dict(
            credentials=dict(
                password="secret",
            ),
        ),
    )

    config = loader(metadata)

    # configuration is loaded as a usual merge
    assert_that(config, is_(equal_to(dict(
        credentials=dict(
            username="default",
            password="secret",
        ),
    ))))

    assert_that(loader.config, is_(equal_to(dict(
        credentials=dict(
            username="default",
        ),
    ))))
    assert_that(loader.secrets, is_(equal_to(dict(
        credentials=dict(
            password="secret",
        ),
    ))))
