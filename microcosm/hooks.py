"""
Object graph hooks.

Provides support for user-defined callbacks during object graph resolution, allowing
user code to be bound to the same scope as the object graph (instead of, for example,
global state or some other singleton).

Example:

    @binding("foo")
    class Foo:
        def __init__(self, graph):
            self.state = None


    def my_hook(foo, state):
        foo.state = state


    on_resolve(Foo, my_hook, "state")


In this case, `func` will be invoked at the time that `Foo` is resolved from the graph; this
will invoke the `my_hook` function and set internal state on the instantiated component.

This pattern is commonly used in conjuction with a decorator to *register* some other state at
graph load time:

    def register(state):
        on_resolve(Foo, my_hook, state)
        return state


    @register
    class Bar:
        passs


"""


ON_RESOLVE = "_microcosm_on_resolve_"


def _invoke_hook(hook_name, target):
    """
    Generic hook invocation.

    """
    try:
        for value in getattr(target, hook_name):
            func, args, kwargs = value
            func(target, *args, **kwargs)
    except AttributeError:
        # no hook defined
        pass
    except (TypeError, ValueError):
        # hook not properly defined (might be a mock)
        pass


def _register_hook(hook_name, target, func, *args, **kwargs):
    """
    Generic hook registration.

    """
    call = (func, args, kwargs)
    try:
        getattr(target, hook_name).append(call)
    except AttributeError:
        setattr(target, hook_name, [call])


def invoke_resolve_hook(target):
    """
    Invoke resolution hook.

    """
    return _invoke_hook(ON_RESOLVE, target)


def on_resolve(target, func, *args, **kwargs):
    """
    Register a resolution hook.

    """
    return _register_hook(ON_RESOLVE, target, func, *args, **kwargs)
