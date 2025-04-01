from ffmpeg_toolkit import types as ffmpeg_types
from pathlib import Path
from pydantic import AnyUrl
from typing import TypedDict, NotRequired

from app.services.my_driver.my_driver_types import MyDriverConfig
from .gp_uploader import Uploader
from ...services import my_driver
from ffmpeg_toolkit import types as ffmpeg_types

type MyDriverConfig = my_driver.types.MyDriverConfig


class UploaderConfig(TypedDict):
    """_summary_

    Args:
        task_name: str
        local_album_path: my_driver.types.DirectoryPath
        GPhoto_url: AnyUrl
        valid_extensions: set[ffmpeg_types.VideoSuffix] | None
        delete_after: bool

    Returns:
        _type_: _description_
    """

    task_name: str
    local_album_path: Path
    GPhoto_url: AnyUrl
    valid_extensions: NotRequired[set[ffmpeg_types.VideoSuffix]]
    delete_after: NotRequired[bool]


class Assignments(TypedDict):
    """_summary_

    Args:
        filename: Path
        assignments: list["GPUploader.GPUploaderTask"]
    """

    filename: Path
    assignments: list[Uploader]
