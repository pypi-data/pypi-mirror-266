import logging

from utils_base.console.constants.COLOR_BACKGROUND import COLOR_BACKGROUND
from utils_base.console.constants.COLOR_FOREGROUND import COLOR_FOREGROUND
from utils_base.console.constants.COLOR_FORMAT import COLOR_FORMAT

LEVEL_TO_STYLE = {
    logging.CRITICAL: dict(
        foreground=COLOR_FOREGROUND.WHITE,
        background=COLOR_BACKGROUND.RED,
        format=COLOR_FORMAT.BOLD,
    ),
    logging.ERROR: dict(
        foreground=COLOR_FOREGROUND.RED,
        background=COLOR_BACKGROUND.BLACK,
    ),
    logging.WARNING: dict(
        foreground=COLOR_FOREGROUND.YELLOW,
        background=COLOR_BACKGROUND.BLACK,
    ),
    logging.INFO: dict(
        foreground=COLOR_FOREGROUND.GREEN,
        background=COLOR_BACKGROUND.BLACK,
    ),
    logging.DEBUG: dict(
        foreground=COLOR_FOREGROUND.WHITE,
        background=COLOR_BACKGROUND.BLACK,
        format=COLOR_FORMAT.FAINT,
    ),
    logging.NOTSET: dict(
        foreground=COLOR_FOREGROUND.WHITE,
        background=COLOR_BACKGROUND.BLACK,
    ),
}
