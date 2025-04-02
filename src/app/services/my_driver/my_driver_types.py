from pathlib import Path
from typing import TypedDict
from .my_driver import BrowserInstances


class MyDriverConfig(TypedDict):
    user_data_dir: Path | None
    browser_executable_path: Path | None
