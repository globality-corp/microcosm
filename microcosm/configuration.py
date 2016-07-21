"""Configuration model and loading"""


class Configuration(dict):
    """
    Nested attribute dictionary with recursive merging for modeling configuration.

    Based on the `easydict` project, but locally modified to remove class attribute
    support (which interferes with adding new member functions) and handle list merging.

    Note that some dict functions (`update`, `pop`) are not correctly implemented,
    but are also not needed (yet).

    """
    def __init__(self, dct=None, **kwargs):
        if dct is None:
            dct = {}
        if kwargs:
            dct.update(**kwargs)

        for key, value in dct.items():
            setattr(self, key, value)

    def __setattr__(self, name, value):
        if isinstance(value, list):
            value = [
                self.__class__(x)
                if isinstance(x, dict) else x for x in value
            ]
        elif isinstance(value, tuple):
            value = tuple(
                self.__class__(x)
                if isinstance(x, dict) else x for x in value
            )
        else:
            value = self.__class__(value) if isinstance(value, dict) else value
        super(Configuration, self).__setattr__(name, value)
        super(Configuration, self).__setitem__(name, value)

    def merge(self, dct=None, **kwargs):
        """
        Recursively merge a dictionary or kwargs into the current dict.

        """
        if dct is None:
            dct = {}
        if kwargs:
            dct.update(**kwargs)

        for key, value in dct.items():
            if all((
                    isinstance(value, dict),
                    isinstance(self.get(key), Configuration),
                    getattr(self.get(key), "__merge__", True),
            )):
                # recursively merge
                self[key].merge(value)
            elif isinstance(value, list) and isinstance(self.get(key), list):
                # append
                self[key] += value
            else:
                # set the new value
                self[key] = value

    __setitem__ = __setattr__
