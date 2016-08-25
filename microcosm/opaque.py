from types import MethodType

from contextdecorator import ContextDecorator

from microcosm.api import binding


class Opaque(object):
    """
    The Opaque collaborator and its assocaited context manager are extremely useful for
    instantiating context specific data during transaction processing. Example:

        from microcosm.opaque import Opaque

        # set up
        def special_opaque_data(some, stuff):
            return "{} {}".format(some, stuff)
        some = "some"
        stuff = "stuff"

        opaque = Opaque()

        # usage
        print opaque.opaque_data_func()

        with opaque.opaque_data(special_opaque_data, some, stuff):
            print opaque.opaque_data_func()

        print opaque.opaque_data_func()

    Outputs:

        {}
        some stuff
        {}


    Note: opaque.opaque_data may also be used as a decorator.

    """
    def __init__(self):
        self.opaque_data = _make_opaque_data(self)

    def _default_data_func(self):
        return {}

    def data_func(self):
        """
        Using the opaque_data context manager in this class, you can override
        the behavior of this function for certain contexts, i.e. in a flask
        request context or in the context of a daemon processing a message.

        Other components which use the `Opaque` collabortor can take advantage
        of this by calling `Opaque.opaque_data_func`, which when used in
        combination with the opaque_data context_manager, can be overriden with
        context-specific behavior.
        """
        return {}


def _make_opaque_data(opaque):
    class OpaqueData(ContextDecorator):
        def __init__(self, opaque_data_func, *args, **kwargs):
            def context_specific_data_func(self):
                return opaque_data_func(*args, **kwargs)
            self.context_specific_data_func = context_specific_data_func

        def __enter__(self):
            opaque.data_func = MethodType(self.context_specific_data_func, opaque)

        def __exit__(self, *exc):
            opaque.data_func = opaque._default_data_func
    return OpaqueData


@binding("opaque")
def configure_opaque(graph):
    return Opaque()
