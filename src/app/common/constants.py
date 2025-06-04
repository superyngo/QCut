import sys
import os
from pathlib import Path
from enum import StrEnum, auto, Enum
from app.common.mytypes import PathEnum
from pydantic import AnyUrl
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv(Path(__file__).parent / ".env")


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


class CONFIG(Enum):
    # 從 .env 載入參數
    TARGET_PATH = (_TARGET_PATH := Path(os.getenv("TARGET_PATH", "")))
    RENDERED_FOLDER_PATH = _TARGET_PATH / "rendered"
    EDGE_PATH = Path(os.getenv("EDGE_PATH", ""))
    BROWSER_CONFIG_FOLDER_NAME = Path(
        APP_PATHS.APP_DATA / os.getenv("BROWSER_CONFIG_FOLDER_NAME")
    )


class ALBUMS_URL(Enum):
    """_summary_

    Args:
        Enum (_type_): _description_
    """

    MOM = AnyUrl(
        "https://photos.google.com/share/AF1QipOjEaSgW_YJxNembwfgYQbouBBHSUyQxFGj2Oq6dpw_EjkWeCBRkSRwczoP7WwoUw"
    )
    MOM_SPEEDUP = AnyUrl(
        "https://photos.google.com/share/AF1QipNG24NndfSGD9rsiHkz7OBvA5amkVOxcadMFI52a0HZR3m9wlUwTgOn5b2h7YBA2Q"
    )
    XIAOMI = AnyUrl(
        "https://photos.google.com/share/AF1QipN5ErAyjjFPCxWgw--uYgbrvJWZu1U39-3iyeChyQQv0PDxU59NnyNP_k4bZNMrvw"
    )
    XIAOMI_SPEEDUP = AnyUrl(
        "https://photos.google.com/share/AF1QipMk6l7y_pzXMh1gTWH5G2lD_U30_Br2E-p2sKDw71YBY97zMh6krVC9cDsT-acFjQ"
    )
