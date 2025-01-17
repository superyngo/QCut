from app import config
from app import mideo_converter
from pathlib import Path


def main() -> None:
    target_path: Path = Path(
        r"D:\Users\user\OneDrive - Chunghwa Telecom Co., Ltd\文件\Projects\Python\sample\tt"
    )
    merge_task_info: mideo_converter.types.MideoMergerTask = {
        "folder_path": target_path,
        "start_hour": 6,
        "delete_after": True,
        "valid_extensions": {mideo_converter.types.VideoSuffix.MP4},
    }
    mideo_converter.merger_handler(**merge_task_info)

    cut_sl_speedup_task_info: mideo_converter.types.CutSlSpeedupTask = {
        "folder_path": target_path,
        "multiple": 0,
        "valid_extensions": {mideo_converter.types.VideoSuffix.MKV},
        "cut_sl_config": {"dB": -20},
    }
    mideo_converter.cut_sl_speedup_handler(**cut_sl_speedup_task_info)


if __name__ == "__main__":
    main()
