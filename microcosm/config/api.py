"""
Configuration API.

"""
from typing import Any

from microcosm.config.model import Configuration
from microcosm.config.validation import validate
from microcosm.metadata import Metadata
from microcosm.typing import Loader


def configure(
    defaults: dict[str, Any],
    metadata: Metadata,
    loader: Loader,
) -> Configuration:
    """
    Build a fresh configuration.

    :params defaults: a nested dictionary of keys and their default values
    :params metadata: the graph metadata
    :params loader: a configuration loader

    """
    config = Configuration(defaults)
    config.merge(loader(metadata))
    validate(defaults, metadata, config)
    return config
