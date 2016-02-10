# Simple Microservice Configuration

Well-written microservices are small and single-purpose; any non-trivial ecosystem will have
a fleet of such services, each performing a different function. Inevitably, these services
will use common code and structure; this library provides a simple mechanism for constructing
these shared components and wiring them together into services.

## Basic Usage

 1. Define factory functions for `components`, attach them to a `namespace`, and provide
    (optional) configuration `defaults`:

        from marquez import defaults, namespace

        @namespace("foo")
        @defaults(baz="value")
        def create_foo(graph, config):
            return dict(bar=graph.bar, baz=config.foo.baz)

        @namespace("bar")
        def create_bar(graph, config):
            return dict()

    Factory functions have access to a directed graph of components (see next) as well as
    configuration data. Default configuration values, if provided, are pre-populated within the
    provided namespace; these may be overridden from data loaded from an external source.

 2. Wire together the service by creating a new graph along with service metadata:

        from marquez import Graph

        graph = Graph(
            name="myservice",
            debug=False,
            testing=False,
        )

    Factories may access the service metadata via `graph.metadata`. This allows for several
    best practices:

     -  Components can implement global conventions (e.g. for logging or persistence), using
        the service name as a discriminator.
     -  Components can customize their behavior during development (`debug=True`) and unit
        testing (`testing=True`)

 3. Reference any `namespace` in the object graph to access the corresponding `component`:

        print graph.foo

    By default, components are initialized *lazily*. In this example, accessing `graph.foo`
    would automatically invoke `create_foo()` and that function's reference to `graph.bar`
    would, in turn, invoke `create_bar()`.

    Graph cycles are not allowed, although dependent components may cache the graph instance
    to access depending components after initialization completes.

 4. Optionally, initialize the service's components explicitly:

        graph.use(
            "foo",
        )

    This construction initializes the listed components up front and then *disables* further
    lazy initializtion, allowing services to catch initialization errors early.
