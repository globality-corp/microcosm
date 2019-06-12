from typing import Callable, Mapping

from microcosm.config.model import Configuration
from microcosm.metadata import Metadata


Loader = Callable[[Metadata], Mapping]
SecondaryLoader = Callable[[Metadata, Configuration], Mapping]
