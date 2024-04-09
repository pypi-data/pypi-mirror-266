"""

AudioKinetic WWise exceptions.

"""

import cozmoai


__all__ = [
    "AudioKineticBaseError",
    "AudioKineticFormatError",
    "AudioKineticIOError",
]


class AudioKineticBaseError(cozmoai.exception.cozmoaiException):
    """ AudioKinetic WWise base error. """
    pass


class AudioKineticFormatError(AudioKineticBaseError):
    """ Invalid file format error. """
    pass


class AudioKineticIOError(AudioKineticBaseError):
    """ File I/O error. """
    pass
