import sys
import os
from pathlib import Path
from enum import StrEnum, auto
from app.common.mytypes import PathEnum


class DEV_INFO(StrEnum):
    APP_NAME = "QCut"
    AUTHOR = "Wenyang Tai"
    COMPANY = "WENANKO"
    APP_VERSION = "0.1.0"
    ADDRESS = "6F.-1, No. 442, Changchun Rd., Songshan Dist., Taipei City 105, Taiwan (R.O.C.)"
    EMAIL = "superyngo@gmail.com"


# set app base path
class APP_PATHS(PathEnum):
    USERPROFILE = Path(os.environ["USERPROFILE"])
    RUNTIME_PATH = Path(os.path.abspath(sys.argv[0])).parent
    BIN = RUNTIME_PATH / "bin"
    PROGRAM_DATA = Path(os.environ["PROGRAMDATA"]) / DEV_INFO.APP_NAME  # C:\ProgramData
    APP_DATA = (
        Path(os.environ["APPDATA"]) / DEV_INFO.APP_NAME
    )  # C:\Users\user\AppData\Roaming
    CONFIG = APP_DATA / "config.conf"
    LOGS = APP_DATA / "Logs"


class ACTIONS(StrEnum):
    """_summary_

    Args:
        StrEnum (_type_): _description_
    """

    CONVERTER = auto()
    SPEEDUP = auto()
    UPLOADER = auto()
