"""
Test validation.

"""
from hamcrest import (
    assert_that,
    calling,
    has_entries,
    raises,
)
from microcosm.api import binding, defaults, load_from_dict, required, typed
from microcosm.config.api import configure
from microcosm.config.types import boolean, comma_separated_list
from microcosm.errors import ValidationError
from microcosm.metadata import Metadata
from microcosm.registry import Registry


class TestValidation:

    def setup(self):
        self.metadata = Metadata("test")
        self.registry = Registry()

    def create_fixture(self, requirement):
        @binding("foo", registry=self.registry)
        @defaults(
            value=requirement,
        )
        def configure_foo(graph):
            return graph.foo.value

    def test_valid(self):
        self.create_fixture(required(int))
        loader = load_from_dict(
            foo=dict(
                value="1",
            ),
        )

        config = configure(self.registry.defaults, self.metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=1,
            ),
        ))

    def test_valid_default(self):
        self.create_fixture(required(int, default_value="1"))
        loader = load_from_dict()

        config = configure(self.registry.defaults, self.metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=1,
            ),
        ))

    def test_invalid_missing(self):
        self.create_fixture(required(int))
        loader = load_from_dict()

        assert_that(
            calling(configure).with_args(self.registry.defaults, self.metadata, loader),
            raises(ValidationError),
        )

    def test_invalid_malformed(self):
        self.create_fixture(required(int))
        loader = load_from_dict(
            foo=dict(
                value="bar",
            ),
        )

        assert_that(
            calling(configure).with_args(self.registry.defaults, self.metadata, loader),
            raises(ValidationError),
        )

    def test_mock_value(self):
        self.create_fixture(required(boolean, mock_value="true"))
        loader = load_from_dict()

        metadata = Metadata("test", testing=True)
        config = configure(self.registry.defaults, metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=True,
            ),
        ))

    def test_comma_separated_list_converted(self):
        self.create_fixture(typed(comma_separated_list, mock_value="abc,def,ghi"))
        loader = load_from_dict()

        metadata = Metadata("test", testing=True)
        config = configure(self.registry.defaults, metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=["abc", "def", "ghi"],
            ),
        ))

    def test_comma_separated_list_empty(self):
        self.create_fixture(typed(comma_separated_list, mock_value=""))
        loader = load_from_dict()

        metadata = Metadata("test", testing=True)
        config = configure(self.registry.defaults, metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=[],
            ),
        ))

    def test_comma_separated_list_unconverted(self):
        self.create_fixture(typed(comma_separated_list, mock_value=["abc", "def", "ghi"]))
        loader = load_from_dict()

        metadata = Metadata("test", testing=True)
        config = configure(self.registry.defaults, metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=["abc", "def", "ghi"],
            ),
        ))

    def test_typed_converted(self):
        self.create_fixture(typed(int))
        loader = load_from_dict(
            foo=dict(
                value="1",
            ),
        )

        config = configure(self.registry.defaults, self.metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=1,
            ),
        ))

    def test_typed_optional(self):
        self.create_fixture(typed(int))
        loader = load_from_dict()

        config = configure(self.registry.defaults, self.metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=None,
            ),
        ))
