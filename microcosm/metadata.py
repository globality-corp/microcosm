"""Service metadata"""


class Metadata(object):
    """
    Service metadata.

    Factories should use service metadata to implement conventions.

    """

    def __init__(self, name, debug=False, testing=False):
        """
        :param name: the name of the microservice
        :param debug: is development debugging enabled?
        :param testing: is unit testing enabled?
        """
        self.name = name
        self.debug = debug
        self.testing = testing
