from collections.abc import Callable
from typing import Any, Union

from microcosm.config.model import Configuration
from microcosm.metadata import Metadata


Component = Union[object, Any]
# NB: Due to covariance / contravariance, we want the return value types to be
# the most general possible, while the parameter types should be the most
# specific. This setup results in these type definitions being as permissive
# as possible. Then within two_stage_loader, we wrap the outputs of the
# loaders in Configuration so that two_stage_loader returns the most specific
# type possible, so that it can be used in as many situations as possible.
Loader = Callable[[Metadata], Configuration]
SecondaryLoader = Callable[[Metadata, Configuration], Configuration]
