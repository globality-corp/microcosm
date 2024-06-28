"""
Test validation.

"""
from hamcrest import (
    assert_that,
    calling,
    empty,
    has_entries,
    raises,
)

from microcosm.api import (
    binding,
    defaults,
    load_from_dict,
    required,
    typed,
)
from microcosm.config.api import configure
from microcosm.config.types import boolean, comma_separated_list
from microcosm.errors import ValidationError
from microcosm.metadata import Metadata
from microcosm.registry import Registry
from microcosm.tests.config.check_warnings import (
    check_no_warnings,
    check_requirements_exactly_one_warning,
    check_unsupported_arg_warning,
)


class TestValidation:

    def setup_method(self):
        self.metadata = Metadata("test")
        self.registry = Registry()

    def create_fixture(self, **config_dict):
        @binding("foo", registry=self.registry)
        @defaults(**config_dict)
        def configure_foo(graph):
            return graph.foo.value

    @check_no_warnings()
    def test_valid(self):
        self.create_fixture(value=required(int))
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

    @check_no_warnings()
    def test_valid_default(self):
        self.create_fixture(value=typed(int, default_value="1"))
        loader = load_from_dict()

        config = configure(self.registry.defaults, self.metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=1,
            ),
        ))

    @check_no_warnings()
    def test_false_default(self):
        self.create_fixture(value=typed(bool, default_value=False))
        loader = load_from_dict()

        config = configure(self.registry.defaults, self.metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=False,
            ),
        ))

    @check_no_warnings()
    def test_nullable(self):
        self.create_fixture(value=typed(
            int,
            default_value=0,
            nullable=True,
            mock_value=None,
        ))
        loader = load_from_dict()

        metadata = Metadata("test", testing=True)
        config = configure(self.registry.defaults, metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=None,
            ),
        ))

    @check_no_warnings()
    def test_nullable_null_default(self):
        self.create_fixture(value=typed(
            int,
            default_value=None,
            nullable=True,
        ))
        loader = load_from_dict()

        config = configure(self.registry.defaults, self.metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=None,
            ),
        ))

    @check_no_warnings()
    def test_null_default_implies_nullable(self):
        self.create_fixture(value=typed(int, default_value=None))
        loader = load_from_dict()

        config = configure(self.registry.defaults, self.metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=None,
            ),
        ))

    @check_no_warnings()
    def test_valid_default_factory(self):
        self.create_fixture(value=typed(list, default_factory=list))
        loader = load_from_dict()

        config = configure(self.registry.defaults, self.metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=empty(),
            ),
        ))

    @check_no_warnings()
    def test_invalid_missing(self):
        self.create_fixture(value=required(int))
        loader = load_from_dict()

        assert_that(
            calling(configure).with_args(self.registry.defaults, self.metadata, loader),
            raises(ValidationError),
        )

    @check_no_warnings()
    def test_invalid_malformed(self):
        self.create_fixture(value=required(int))
        loader = load_from_dict(
            foo=dict(
                value="bar",
            ),
        )

        assert_that(
            calling(configure).with_args(self.registry.defaults, self.metadata, loader),
            raises(ValidationError),
        )

    @check_no_warnings()
    def test_invalid_none(self):
        self.create_fixture(value=required(int))
        loader = load_from_dict(
            foo=dict(
                value=None,
            ),
        )

        assert_that(
            calling(configure).with_args(self.registry.defaults, self.metadata, loader),
            raises(ValidationError),
        )

    @check_no_warnings()
    def test_mock_value(self):
        self.create_fixture(value=required(boolean, mock_value="true"))
        loader = load_from_dict()

        metadata = Metadata("test", testing=True)
        config = configure(self.registry.defaults, metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=True,
            ),
        ))

    @check_no_warnings()
    def test_comma_separated_list_converted(self):
        self.create_fixture(value=required(comma_separated_list, mock_value="abc,def,ghi"))
        loader = load_from_dict()

        metadata = Metadata("test", testing=True)
        config = configure(self.registry.defaults, metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=["abc", "def", "ghi"],
            ),
        ))

    @check_no_warnings()
    def test_comma_separated_list_empty(self):
        self.create_fixture(value=required(comma_separated_list, mock_value=""))
        loader = load_from_dict()

        metadata = Metadata("test", testing=True)
        config = configure(self.registry.defaults, metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=[],
            ),
        ))

    @check_no_warnings()
    def test_comma_separated_list_unconverted(self):
        self.create_fixture(value=required(comma_separated_list, mock_value=["abc", "def", "ghi"]))
        loader = load_from_dict()

        metadata = Metadata("test", testing=True)
        config = configure(self.registry.defaults, metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=["abc", "def", "ghi"],
            ),
        ))

    @check_no_warnings()
    def test_typed_converted(self):
        self.create_fixture(value=required(int))
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

    @check_no_warnings()
    def test_boolean_typed_converted(self):
        self.create_fixture(
            bar=typed(bool, default_value=None),
            baz=typed(bool, default_value=None),
            qux=typed(bool, default_value=None),
            kog=typed(bool, default_value=None),
        )
        loader = load_from_dict(
            foo=dict(
                bar="False",
                baz="True",
                qux="false",
                kog="true",
            ),
        )

        config = configure(self.registry.defaults, self.metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                bar=False,
                baz=True,
                qux=False,
                kog=True,
            ),
        ))

    @check_requirements_exactly_one_warning()
    def test_missing_default(self):
        self.create_fixture(value=typed(int))
        loader = load_from_dict()

        config = configure(self.registry.defaults, self.metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=None,
            ),
        ))

    @check_requirements_exactly_one_warning()
    def test_default_and_required(self):
        self.create_fixture(value=required(int, default_value="1"))
        loader = load_from_dict()

        config = configure(self.registry.defaults, self.metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=1,
            ),
        ))

    @check_unsupported_arg_warning()
    def test_unsupported_arg(self):
        self.create_fixture(value=required(int, mock_value=0, spaghetti="foo"))
        loader = load_from_dict()

        metadata = Metadata("test", testing=True)
        config = configure(self.registry.defaults, metadata, loader)
        assert_that(config, has_entries(
            foo=has_entries(
                value=0,
            ),
        ))

    def test_default_factory_and_required_error(self):
        assert_that(
            calling(required).with_args(list, default_factory=list),
            raises(ValueError),
        )

    def test_default_and_default_factory_error(self):
        assert_that(
            calling(typed).with_args(list, default_value=["foo"], default_factory=list),
            raises(ValueError),
        )

    def test_default_default_factory_and_required_error(self):
        assert_that(
            calling(required).with_args(list, default_value=["foo"], default_factory=list),
            raises(ValueError),
        )
