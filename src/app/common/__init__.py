from logging import Logger
import os
from . import constants
from . import mytypes
from .my_logger import setup_logger

# Create App directories if they don't exist
# constants.AppPaths.PROGRAM_DATA.mkdir(parents=True, exist_ok=True)
constants.APP_PATHS.APP_DATA.mkdir(parents=True, exist_ok=True)

# Create logger
logger: Logger = setup_logger(constants.APP_PATHS.LOGS)

os.environ["PYTHONUTF8"] = "1"
os.environ["PATH"] = os.pathsep.join(
    [
        str(constants.APP_PATHS.RUNTIME_PATH),
        str(constants.APP_PATHS.BIN),
        os.environ["PATH"],
    ]
)
__all__: list[str] = ["constants", "mytypes", "logger"]
