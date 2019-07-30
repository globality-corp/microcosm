from jaeger_client.config import (
    DEFAULT_REPORTING_HOST,
    DEFAULT_REPORTING_PORT,
    DEFAULT_SAMPLING_PORT,
    Config,
)

from microcosm.api import binding, defaults, typed
from microcosm.config.types import boolean


SPAN_NAME = "span_name"


@binding("tracer")
@defaults(
    sample_type="ratelimiting",
    sample_param=typed(int, 10),
    sampling_port=typed(int, DEFAULT_SAMPLING_PORT),
    reporting_port=typed(int, DEFAULT_REPORTING_PORT),
    reporting_host=DEFAULT_REPORTING_HOST,
    logging_enabled=typed(boolean, False),
)
def configure_tracing(graph):
    """
    See https://www.jaegertracing.io/docs/1.12/sampling/ for more info about
    available sampling strategies.

    """
    config = Config(
        config={
            "sampler": {
                "type": graph.config.tracer.sample_type,
                "param": graph.config.tracer.sample_param,
            },
            "local_agent": {
                "sampling_port": graph.config.tracer.sampling_port,
                "reporting_port": graph.config.tracer.reporting_port,
                "reporting_host": graph.config.tracer.reporting_host,
            },
            "logging": graph.config.tracer.logging_enabled,
        },
        service_name=graph.metadata.name,
    )
    return config.initialize_tracer()
