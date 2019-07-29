"""
Configuration modeling, loading, and validation.

"""
from warnings import warn

from microcosm.config.sentinel import UNSET
from microcosm.errors import ValidationError


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


class Requirement:
    """
    A value type for configuration defaults that represents *expected* config.

    """
    def __init__(
        self,
        type=str,
        default_value=UNSET,
        mock_value=UNSET,
        required=True,
        default_factory=None,
        nullable=False,
        *args,
        **kwargs,
    ):
        """
        :param type: a type callable
        :param mock_value: a default value to use durint testing (only)

        """
        self.type = type
        self.default_value = default_value
        self.default_factory = default_factory
        self.mock_value = mock_value
        self.required = required
        self.nullable = nullable or (default_value is None)

        if kwargs:
            warn(
                f"Unsupported `Requirement` args {kwargs}.  "
                "Support for arbitrary arguments to `Requirement` will be dropped",
                category=FutureWarning,
            )

        if default_factory is None and required == (default_value is not UNSET):
            # Warn when the user doesn't provide exactly one of
            #
            # [`required=True`, `default_value=...`]
            #
            # When the user is not using `default_factory`, this could be legacy
            # code, so we just warn. In the future we will remove this clause
            # and just use the error clause below, but for now we just warn in
            # those situations which could occur as of the time this was
            # introduced
            warn(
                "Must either specify `required=True` or provide default value.",
                category=FutureWarning,
            )
        elif any([
            # Must either require a value or provide a default
            all([
                not required,
                default_value is UNSET,
                default_factory is None,
            ]),

            # Can't require a value and also specify a default
            required and any([
                default_value is not UNSET,
                default_factory is not None,
            ]),

            # Can't specify both a default value and a default factory
            all([
                default_value is not UNSET,
                default_factory is not None,
            ]),
        ]):
            # For all situations where user doesn't provide exactly one of
            #
            # [`required=True`, `default_value=...`, `default_factory=...`]
            #
            # and it's using newly introduced features, we error, so that new
            # issues can't be introduced going forward.  In the future, we will
            # just perform this check and remove the warning above
            raise ValueError(
                "Expected exactly one of "
                "[default_value, default_factory, required], "
                f"but got {[default_value, default_factory, required]}"
            )

    def validate(self, metadata, path, value):
        """
        Validate this requirement.

        """
        if isinstance(value, Requirement):
            # if the RHS is still a Requirement object, it was not set
            if metadata.testing and self.mock_value is not UNSET:
                value = self.mock_value
            elif self.default_value is not UNSET:
                value = self.default_value
            elif self.default_factory is not None:
                value = self.default_factory()
            elif not value.required:
                return None
            else:
                raise ValidationError(f"Missing required configuration for: {'.'.join(path)}")

        try:
            if value is None and self.nullable:
                return value

            return self.type(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Missing required configuration for: {'.'.join(path)}: {value}")
