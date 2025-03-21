from app import mideo_converter
from pathlib import Path


def main() -> None:
    target_path: Path = Path(r"D:\smb\xiaomi\xiaomi_camera_videos\94f827b4b94e")
    merge_task_info: mideo_converter.types.MideoMergerTask = {
        "folder_path": target_path,
        "start_hour": 6,
        "delete_after": True,
    }
    mideo_converter.merger_handler(**merge_task_info)

    cut_sl_speedup_task_info: mideo_converter.types.CutSlSpeedupTask = {
        "folder_path": target_path,
        "multiple": 0,
        "same_encode": False,
    }
    mideo_converter.cut_sl_speedup_handler(**(cut_sl_speedup_task_info))


if __name__ == "__main__":
    main()
