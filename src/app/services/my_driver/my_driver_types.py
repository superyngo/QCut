from pathlib import Path
from typing import TypedDict


class MyDriverConfig(TypedDict):
    user_data_dir: Path | None
    browser_executable_path: Path | None
