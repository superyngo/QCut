from .actions import mideo_converter, GPhoto_uploader
from . import utils
from .common import logger, constants
from .services.my_driver import browser_instances

# from .actions.GPhoto_uploader.gp_uploader import upload_handler

# Create App directories if they don't exist
constants.APP_PATHS.PROGRAM_DATA.mkdir(parents=True, exist_ok=True)
constants.APP_PATHS.APP_DATA.mkdir(parents=True, exist_ok=True)


__all__: list[str] = [
    "constants",
    "utils",
    "logger",
    "mideo_converter",
    "GPhoto_uploader",
    "browser_instances",
]
