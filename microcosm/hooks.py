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
from collections.abc import Callable
from typing import Any


ON_RESOLVE = "_microcosm_on_resolve_"


def _get_hook_name(hook_prefix: str, target_cls: type):
    return f"{hook_prefix}_{target_cls.__name__}"


def _invoke_hook(hook_prefix: str, target_component: Any) -> None:
    """
    Generic hook invocation.

    """
    hook_name = _get_hook_name(hook_prefix, target_component.__class__)
    try:
        for value in getattr(target_component, hook_name):
            func, args, kwargs = value
            func(target_component, *args, **kwargs)
    except AttributeError:
        # no hook defined
        pass
    except (TypeError, ValueError):
        # hook not properly defined (might be a mock)
        pass


def _register_hook(hook_prefix: str, target_cls: type, func: Callable[[Any, Any], None], *args, **kwargs) -> None:
    """
    Generic hook registration.

    """
    hook_name = _get_hook_name(hook_prefix, target_cls)
    call = (func, args, kwargs)
    try:
        getattr(target_cls, hook_name).append(call)
    except AttributeError:
        setattr(target_cls, hook_name, [call])


def invoke_resolve_hook(target: Any) -> None:
    """
    Invoke resolution hook.

    """
    return _invoke_hook(ON_RESOLVE, target)


def on_resolve(target: Any, func: Callable[..., None], *args, **kwargs) -> None:
    """
    Register a resolution hook.

    """
    return _register_hook(ON_RESOLVE, target, func, *args, **kwargs)
