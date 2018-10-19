# Simple Microservice Configuration

Well-written microservices are small and single-purpose; any non-trivial ecosystem will have
a fleet of such services, each performing a different function. Inevitably, these services
will use common code and structure; this library provides a simple mechanism for constructing
these shared components and wiring them together into services.

[![Circle CI](https://circleci.com/gh/globality-corp/microcosm/tree/develop.svg?style=svg)](https://circleci.com/gh/globality-corp/microcosm/tree/develop)


## Terminology

 -  A `microservice` is a small software application. It is composed of several smaller pieces
    of software, many of which are reusable.
 -  A `component` is one of these (possibly reusable) pieces of software.
 -  A `factory` is a function used to create a component; it may be an object's constructor.
 -  A `config dict` is a nested dictionary with string-valued keys. It contains data used
    by factories to create components.
 -  An `object graph` is a collection of components that may reference each other (acyclically).
 -  A `binding` is a string-valued key. It is used to identify a component within an object graph
    and the subsection of the config dict reserved for a component's factory.


## Basic Usage

 1. Define factory functions for `components`, attach them to a `binding`, and provide
    (optional) configuration `defaults`:

        from microcosm.api import defaults, binding

        @binding("foo")
        @defaults(baz="value")
        def create_foo(graph):
            return dict(
                # factories can reference other components
                bar=graph.bar,
                # factories can reference configuration
                baz=graph.config.foo.baz,
            )

        @binding("bar")
        def create_bar(graph):
            return dict()

    Factory functions have access to the `object graph` and, through it, the `config dict`. Default
    configuration values, if provided, are pre-populated within the provided binding; these may be
    overridden from data loaded from an external source.

 2. Wire together the microservice by creating a new object graph along with service metadata:

        from microcosm.api import create_object_graph

        graph = create_object_graph(
            name="myservice",
            debug=False,
            testing=False,
        )

    Factories may access the service metadata via `graph.metadata`. This allows for several
    best practices:

     -  Components can implement ecosystem-wide conventions (e.g. for logging or persistence),
        using the service name as a discriminator.
     -  Components can customize their behavior during development (`debug=True`) and unit
        testing (`testing=True`)

 3. Reference any `binding` in the `object graph` to access the corresponding `component`:

        print(graph.foo)

    Components are initialized *lazily*. In this example, the first time `graph.foo` is accessed,
    the bound factory (`create_foo()`) is automatically invoked. Since this factory in turn
    accesses `graph.bar`, the next factory in the chain (`create_bar()`) would also be called
    if it had not been called yet.

    Graph cycles are not allowed, although dependent components may cache the graph instance
    to access depending components after initialization completes.

 4. Optionally, initialize the microservice's components explicitly:

        graph.use(
            "foo",
            "bar",
        )

    While the same effect could be achieved by accessing `graph.foo` or `graph.bar`, this
    construction has the advantage of initializes the listed components up front and triggering
    any configuration errors as early as possible.

    It is also possible to then *disable* any subsequent lazy initialization, preventing any
    unintended initialization during subsequent operations:

        graph.lock()


## Assumptions

This library was influenced by the [pinject](https://github.com/google/pinject) project, but
makes a few assumption that allow for a great deal of simplication:

 1. Microservices are small enough that simple string bindings suffice. Or, put another way,
    conflicts between identically bound components are a non-concern and there is no need
    for explicit scopes.

 2. Microservices use processes, not threads to scale. As such, thread synchronization is
    a non-goal.

 3. Mocking (and patching) of the object graph is important and needs to be easy. Unit tests
    expect to use `unittest.mock library; it should be trivial to temporarily replace a component.

 4. Some components will be functions that modify other components rather than objects
    that need to be instantiated.
