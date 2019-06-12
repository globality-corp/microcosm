from typing import Callable

from microcosm.config.model import Configuration
from microcosm.metadata import Metadata


Loader = Callable[[Metadata], Configuration]
DerivativeLoader = Callable[[Metadata, Configuration], Configuration]
