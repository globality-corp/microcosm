"""
Decorator the allows a factory to use scoping.

"""
from microcosm.decorators import binding
from microcosm.scoping.factories import ScopedFactory


def scoped_binding(key, default_scope=None, registry=None):
    def decorator(func):
        binding(key, registry)(ScopedFactory(key, func, default_scope))
        return func
    return decorator
