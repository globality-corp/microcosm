import warnings
from contextlib import contextmanager

from hamcrest import (
    assert_that,
    contains_string,
    empty,
    equal_to,
    has_length,
    is_,
)


@contextmanager
def check_warning(message):
    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")

        yield

        assert_that(caught_warnings, has_length(1))
        warning = caught_warnings[-1]

        assert_that(str(warning.message), contains_string(message))
        assert_that(warning.category, is_(equal_to(FutureWarning)))


def check_requirements_exactly_one_warning():
    return check_warning("Must either")


def check_unsupported_arg_warning():
    return check_warning("Unsupported")


@contextmanager
def check_no_warnings():
    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")

        yield

        caught_warnings = [warning for warning in caught_warnings if "virtualenvs" not in warning.filename]
        if caught_warnings:
            assert_that(caught_warnings, is_(empty()), caught_warnings[-1].message)
