"""
Error types

"""


class AlreadyBoundError(Exception):
    """
    Raised if a factory is already bound to a name.

    """
    pass


class CyclicGraphError(Exception):
    """
    Raised if a graph has a cycle.

    """
    pass


class LockedGraphError(Exception):
    """
    Raised when attempting to create a component in a locked object graph.

    """
    pass


class NotBoundError(Exception):
    """
    Raised if not factory is bound to a name.

    """
    pass


class ValidationError(Exception):
    """
    Raised if a configuration value fails validation.

    """
    pass
