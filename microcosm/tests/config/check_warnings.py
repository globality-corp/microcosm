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
def check_requirements_exactly_one_warning(expect_string):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        yield

        assert_that(w, has_length(1))
        warning = w[-1]

        assert_that(str(warning.message), contains_string(expect_string))
        assert_that(warning.category, is_(equal_to(FutureWarning)))


@contextmanager
def check_no_warnings():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        yield

        if w:
            assert_that(w, is_(empty()), w[-1].message)
