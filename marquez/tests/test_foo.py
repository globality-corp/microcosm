"""Test placeholder"""
from hamcrest import assert_that, equal_to, is_


def test_tautology():
    assert_that(1, is_(equal_to(1)))
