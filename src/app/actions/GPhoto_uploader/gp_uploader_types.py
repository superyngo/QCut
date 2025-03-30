from typing import TypedDict, NotRequired
from pathlib import Path
from pydantic import AnyUrl


class GPUploaderTask(TypedDict):
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
