from typing import Callable, Mapping

from microcosm.config.model import Configuration
from microcosm.metadata import Metadata


# NB: Due to covariance / contravariance, we want the return value types to be
# the most general possible, while the parameter types should be the most
# specific. This setup results in these type definitiions being as permissive
# as possible. Then within two_stage_loader, we wrap the outputs of the
# loaders in Configuration so that two_stage_loader returns the most specific
# type possible, so that it can be used in as many situations as possible.
Loader = Callable[[Metadata], Mapping]
SecondaryLoader = Callable[[Metadata, Configuration], Mapping]
