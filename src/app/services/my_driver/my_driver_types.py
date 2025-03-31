from pathlib import Path
from typing import TypedDict, NotRequired


class DriverConfig(TypedDict):
    user_data_dir: NotRequired[Path]
    browser_executable_path: NotRequired[Path]
