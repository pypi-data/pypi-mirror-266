
import logging


__all__ = [
    "logger",
    "logger_protocol",
    "logger_robot",
    "logger_reaction",
    "logger_behavior",
    "logger_animation",
]


# General logger - general cozmoai log messages.
logger = logging.getLogger("cozmoai.general")
# Protocol logger - log messages related to the Cozmo protocol.
logger_protocol = logging.getLogger("cozmoai.protocol")
# Robot logger - log messages coming from the robot microcontrollers.
logger_robot = logging.getLogger("cozmoai.robot")
# Reaction logger.
logger_reaction = logging.getLogger("cozmoai.reaction")
# Behavior logger.
logger_behavior = logging.getLogger("cozmoai.behavior")
# Animation logger.
logger_animation = logging.getLogger("cozmoai.animation")

# TODO: See cozmo_resources/config/engine/console_filter_config.json
