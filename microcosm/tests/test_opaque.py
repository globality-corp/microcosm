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


def test_collaboration():
    """
    This test is intended to show how to use Opaque with other microcosm components. Here `Apple` is
    a component that benefits from context awareness, but it does not know where it will be
    called from.

    The Juicer will call the Apple while in its special context. Because the Apple has a
    reference to opaque and the Juicer's class function uses opaque.bind to apply context to it
    the Apple is able to refer to the context it is being called from.

    """
    opaque = Opaque()
    opaque['some'] = 'cool stuff'

    class Apple(object):
        def __init__(self, context):
            self.opaque = context

        def show_opaque(self):
            return self.opaque.as_dict()

    class Juicer(object):
        def __init__(self, apple):
            self.apple = apple

        def do_work(self):
            return apple.show_opaque()

    apple = Apple(opaque)
    juicer = Juicer(apple)

    decorated_work = opaque.bind(
        special_context_function, 'some', 'stuff'
    )(juicer.do_work)

    assert_that(opaque.as_dict(), is_(equal_to(dict(some='cool stuff'))))
    assert_that(decorated_work(), is_(equal_to(special_context_function('some', 'stuff'))))
    assert_that(opaque.as_dict(), is_(equal_to(dict(some='cool stuff'))))
