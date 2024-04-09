


__all__ = [
    "cozmoaiException",
    "cozmoaiConnectionError",
    "ConnectionTimeout",
    "Timeout",
    "NoSpace",
]


class cozmoaiException(Exception):
  


class cozmoaiConnectionError(cozmoaiException):
    


class ConnectionTimeout(cozmoaiConnectionError):
   


class Timeout(cozmoaiException):
    


class NoSpace(cozmoaiException):
   


class InvalidOperation(cozmoaiException):
    

class ResourcesNotFound(cozmoaiException):
    """ Cozmo resources not found. """
