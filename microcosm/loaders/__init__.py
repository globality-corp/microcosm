"""
Configuration loading

A configuration loader is any function that accepts `Metadata` and
returns a `dict` (or `Configuration` model).

Configuration might be loaded from a file, from environment variables,
or from an external service.

"""
from microcosm.loaders.compose import (  # noqa: F401
    load_each,
)
from microcosm.loaders.environment import (  # noqa: F401
    load_from_environ,
    load_from_environ_as_json,
)
from microcosm.loaders.keys import (  # noqa: F401
    expand_config,
)
from microcosm.loaders.settings import (  # noqa: F401
    load_from_json_file,
)


def load_from_dict(dct=None, **kwargs):
    """
    Load configuration from a dictionary.

    """
    dct = dct or dict()
    dct.update(kwargs)

    def _load_from_dict(metadata):
        return dict(dct)
    return _load_from_dict
