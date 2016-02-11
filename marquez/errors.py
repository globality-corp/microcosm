"""Error types"""


class AlreadyBoundError(Exception):
    """
    Raised if a factory is already bound to a name.

    """
    pass


class NotBoundError(Exception):
    """
    Raised if not factory is bound to a name.

    """
    pass
