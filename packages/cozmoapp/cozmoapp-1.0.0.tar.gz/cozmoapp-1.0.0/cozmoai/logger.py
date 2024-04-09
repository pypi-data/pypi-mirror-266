
import logging


__all__ = [
    "logger",
    "logger_protocol",
    "logger_robot",
    "logger_reaction",
    "logger_behavior",
    "logger_animation",
]



logger = logging.getLogger("cozmoai.general")

logger_protocol = logging.getLogger("cozmoai.protocol")

logger_robot = logging.getLogger("cozmoai.robot")

logger_reaction = logging.getLogger("cozmoai.reaction")

logger_behavior = logging.getLogger("cozmoai.behavior")

logger_animation = logging.getLogger("cozmoai.animation")

