from jaeger_client import Config

from microcosm.api import binding, defaults, typed


@binding("tracer")
@defaults(
    sample_type="ratelimiting",
    sample_param=typed(int, 10),
)
def configure_tracing(graph):
    """
    See https://www.jaegertracing.io/docs/1.12/sampling/ for more info about
    available sampling strategies.

    """
    config = Config(
        config={
            'sampler': {
                'type': graph.config.tracer.sample_type,
                'param': graph.config.tracer.sample_param,
            },
            'logging': True,
        },
        service_name=graph.metadata.name,
    )
    return config.initialize_tracer()
