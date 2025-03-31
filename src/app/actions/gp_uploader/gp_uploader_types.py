from typing import TypedDict, NotRequired
from pathlib import Path
from pydantic import AnyUrl
from app.services.my_driver.my_driver_types import DriverConfig
from .gp_uploader import Uploader


class GPUploaderConfig(TypedDict):
    """_summary_

    Args:
        name: str
        local_album_path: Path
        GPhoto_url: AnyUrl
        delete_after: NotRequired[bool]
    """

    name: str
    local_album_path: Path
    GPhoto_url: AnyUrl
    delete_after: NotRequired[bool]


class Assignments(TypedDict):
    """_summary_

    Args:
        filename: Path
        assignments: list["GPUploader.GPUploaderTask"]
    """

    filename: Path
    assignments: list[Uploader]
