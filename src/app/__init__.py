from .actions import mideo_converter, gp_uploader
from .common import constants, logger
from . import utils

# from .actions.GPhoto_uploader.gp_uploader import upload_handler

# Create App directories if they don't exist
constants.APP_PATHS.PROGRAM_DATA.mkdir(parents=True, exist_ok=True)
constants.APP_PATHS.APP_DATA.mkdir(parents=True, exist_ok=True)


__all__: list[str] = [
    "constants",
    "logger",
    "utils",
    "mideo_converter",
    "gp_uploader",
]
