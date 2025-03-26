from app import mideo_converter
from pathlib import Path


def main() -> None:
    target_path: Path = Path(r"C:\Users\user\Downloads")
    mideo_converter.MergeByDate(
        input_folder_path=target_path,
        valid_extensions={mideo_converter.VideoSuffix.MP4},
        walkthrough=True,
        delete_after=False,
        start_hour=6,
    ).merge()

    mideo_converter.BatchVideoRender(
        input_folder_path=target_path,
        output_folder_path=target_path / "cut_sl",
        valid_extensions={mideo_converter.VideoSuffix.MKV},
        walkthrough=False,
        delete_after=False,
    ).apply(task=mideo_converter.ffmpeg_toolkit.PARTIAL_TASKS.cut_silence(dB=-15))


if __name__ == "__main__":
    main()
