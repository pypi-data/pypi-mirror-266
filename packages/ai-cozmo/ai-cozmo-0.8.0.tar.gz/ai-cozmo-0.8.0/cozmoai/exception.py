


__all__ = [
    "cozmoaiException",
    "cozmoaiConnectionError",
    "ConnectionTimeout",
    "Timeout",
    "NoSpace",
]


class cozmoaiException(Exception):
    """ Base class for all cozmoai exceptions. """


class cozmoaiConnectionError(cozmoaiException):
    """ Base class for all cozmoai connection exceptions. """


class ConnectionTimeout(cozmoaiConnectionError):
    """ Connection timeout. """


class Timeout(cozmoaiException):
    """ Operation timed out. """


class NoSpace(cozmoaiException):
    """ Out of space. """


class InvalidOperation(cozmoaiException):
    """ Invalid operation. """


class ResourcesNotFound(cozmoaiException):
    """ Cozmo resources not found. """
