from contextlib import contextmanager
from os import environ
from tempfile import NamedTemporaryFile


@contextmanager
def envvar(key, value):
    """
    Temporarily set an environment variable.

    """
    old_value = environ.get(key)
    environ[key] = value
    yield
    if old_value is None:
        del environ[key]
    else:
        environ[key] = value


@contextmanager
def settings(data):
    """
    Temporarily create a temporary file.

    """
    configfile_ = NamedTemporaryFile(mode='w+')
    configfile_.write(data)
    configfile_.flush()
    yield configfile_
