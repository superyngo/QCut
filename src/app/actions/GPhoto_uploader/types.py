from typing import TypedDict, NotRequired
from pathlib import Path
from app.services import MyDriver


class UploaderTask(TypedDict):
    name: str
    local_album_path: Path
    GPhoto_url: str
    mkv_files: NotRequired[list[Path]]
    driver: MyDriver
    delete_after: NotRequired[bool]
