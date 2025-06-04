from superyngo_logger import init_logger, clean_logs
from logging import Logger
import os
from . import constants
from . import mytypes

# Create App directories if they don't exist
# constants.AppPaths.PROGRAM_DATA.mkdir(parents=True, exist_ok=True)
constants.APP_PATHS.APP_DATA.mkdir(parents=True, exist_ok=True)

# Create logger
logger: Logger = init_logger(constants.APP_PATHS.LOGS)
clean_logs(log_dir=constants.APP_PATHS.LOGS.value, days_count=10)

os.environ["PYTHONUTF8"] = "1"
os.environ["PATH"] = os.pathsep.join(
    [
        str(constants.APP_PATHS.RUNTIME_PATH),
        str(constants.APP_PATHS.BIN),
        os.environ["PATH"],
    ]
)
__all__: list[str] = ["constants", "mytypes", "logger"]
