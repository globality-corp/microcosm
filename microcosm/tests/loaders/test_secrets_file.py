import json

from hamcrest import (
    assert_that,
    equal_to,
    is_,
    none,
)

from microcosm.loaders.secrets_file import get_config_filename, load_from_json_secrets_file
from microcosm.metadata import Metadata
from microcosm.tests.loaders.fixtures import envvar, settings


def test_get_secrets_file_path():
    metadata = Metadata("foo-dow")
    result = get_config_filename(metadata)
    assert_that(result, is_(none()))

    assert_path = "/secrets/secret_file.json"
    with envvar("FOO_DOW__SECRETS", assert_path):
        result = get_config_filename(metadata)
        assert_that(result, is_(equal_to(assert_path)))


def test_unset_load_secrets_from_file():
    metadata = Metadata("foo-dow")
    result = load_from_json_secrets_file(metadata)
    assert_that(result, is_({}))


def test_load_secrets_from_file():
    metadata = Metadata("foo")

    expected_secret_config = {
        "mock_secret": "abc_123",
        "some_other_mock_secret": {"stuff": "abc", "things": "test"},
    }

    with settings(json.dumps(expected_secret_config)) as secret_settings_:
        with envvar("FOO__SECRETS", secret_settings_.name):
            results = load_from_json_secrets_file(metadata)

    assert_that(results, is_(equal_to(expected_secret_config)))
