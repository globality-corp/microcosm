from hamcrest import assert_that, equal_to, is_

from microcosm.loaders.keys import expand_config


def test_expand_config():
    """
    Configuration expansion should work.

    """
    assert_that(
        expand_config(
            {
                "prefix.foo": "bar",
                "prefix.BAR.baz": lambda: "foo",
                "this": "that",
            },
            key_parts_filter=lambda key_parts: key_parts[0] == "prefix",
            skip_to=1,
            value_func=lambda value: value() if callable(value) else value,
        ),
        is_(equal_to(
            {
                "foo": "bar",
                "bar": {
                    "baz": "foo",
                },
            },
        )),
    )
