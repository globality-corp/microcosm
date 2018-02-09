"""
Configuration annotations.

"""
from distutils.util import strtobool


def boolean(value):
    """
    Annotate a value as boolean.

    """
    if value == "":
        return False
    return strtobool(value)


def required(value):
    """
    Annotate a value as required.

    """
    if value is None:
        raise Exception("Missing required value")
    return value


def must_override(metadata, value):
    """
    Annotate a value as required outside of unit testing.

    """
    if metadata.testing:
        return value

    return required(value)


def evaluate(metadata, annotations, config):
    """
    Evaluate a set of annotations against a `Configuration`.

    """
    keys = set(annotations.keys()) | set(config.keys())
    for key in keys:
        annotation = annotations.get(key)
        target = config.get(key)

        try:
            value = evaluate_one(metadata, key, annotation, target)
        except Exception as error:
            print(f"Unable to load configuration for '{key}': {target}")  # noqa
            raise

        config[key] = value

    return config


def split(dct):
    """
    Split inputs into data and annotations.

    """
    data, annotations = dict(), dict()

    for key, value in dct.items():
        if isinstance(value, dict):
            data[key], annotations[key] = split(value)
        elif callable(value):
            annotations[key] = value
        else:
            data[key] = value

    return data, annotations


def evaluate_one(metadata, key, annotation, target):
    """
    Evaluate a single annotation against its target.

    """
    if annotation is None:
        return target

    if isinstance(annotation, dict):
        if not isinstance(target, dict):
            raise Exception("Expected dictionary")

        subkeys = set(annotation.keys()) | set(target.keys())
        return {
            subkey: evaluate_one(
                metadata,
                subkey,
                annotation.get(subkey),
                target.get(subkey),
            )
            for subkey in subkeys
        }
    elif annotation is None:
        return target
    else:
        try:
            return annotation(target)
        except TypeError:
            return annotation(metadata, target)
