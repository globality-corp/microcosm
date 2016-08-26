from hamcrest import (
    assert_that,
    equal_to,
    is_,
)

from microcosm.opaque import Opaque


def special_context_function(some, stuff):
    return dict(some=some, stuff=stuff)


def test_basic_usage():
    opaque = Opaque()
    assert_that(opaque.as_dict(), is_(equal_to(dict())))

    opaque['foo'] = 'bar'
    assert_that(opaque.as_dict(), is_(equal_to(dict(foo='bar'))))
    assert_that(opaque['foo'], is_(equal_to('bar')))


def test_context_manager():
    opaque = Opaque()

    opaque['some'] = 'cool stuff'
    assert_that(opaque.as_dict(), is_(equal_to(dict(some='cool stuff'))))

    with opaque.bind(special_context_function, 'some', 'stuff'):
        assert_that(opaque.as_dict(), is_(equal_to(special_context_function('some', 'stuff'))))
        assert_that(opaque.as_dict(), is_(equal_to(dict(some='some', stuff='stuff'))))
    with opaque.bind(special_context_function, 'some', 'stuff'):
        assert_that(opaque.as_dict(), is_(equal_to(special_context_function('some', 'stuff'))))
        assert_that(opaque.as_dict(), is_(equal_to(dict(some='some', stuff='stuff'))))

    assert_that(opaque.as_dict(), is_(equal_to(dict(some='cool stuff'))))


def test_decorator():
    opaque = Opaque()
    opaque['some'] = 'cool stuff'

    @opaque.bind(special_context_function, 'some', 'stuff')
    def function_to_decorate():
        return opaque.as_dict()

    assert_that(opaque.as_dict(), is_(equal_to(dict(some='cool stuff'))))
    assert_that(function_to_decorate(), is_(equal_to(special_context_function('some', 'stuff'))))
    assert_that(opaque.as_dict(), is_(equal_to(dict(some='cool stuff'))))
    assert_that(function_to_decorate(), is_(equal_to(special_context_function(some='some', stuff='stuff'))))
    assert_that(opaque.as_dict(), is_(equal_to(dict(some='cool stuff'))))


def test_nesting():
    opaque = Opaque()

    opaque['some'] = 'cool stuff'

    assert_that(opaque.as_dict(), is_(equal_to(dict(some='cool stuff'))))
    with opaque.bind(special_context_function, 'some', 'stuff'):
        assert_that(opaque.as_dict(), is_(equal_to(special_context_function('some', 'stuff'))))
        with opaque.bind(special_context_function, 'some more', 'stuff'):
            assert_that(opaque.as_dict(), is_(equal_to(special_context_function('some more', 'stuff'))))
        assert_that(opaque.as_dict(), is_(equal_to(special_context_function('some', 'stuff'))))
    assert_that(opaque.as_dict(), is_(equal_to(dict(some='cool stuff'))))
