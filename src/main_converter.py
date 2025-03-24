from app import mideo_converter
from pathlib import Path
import re


def main() -> None:
    target_path: Path = Path(r"C:\Users\user\Downloads")
    merged_dir = target_path / "merged"

    mideo_converter.MergeByDate(
        input_folder_path=target_path,
        output_folder_path=merged_dir,
        valid_extensions={mideo_converter.VideoSuffix.MP4},
        walkthrough=True,
        delete_after=False,
        timestamp_pattern=mideo_converter.RE_PATTERN.DATETIMESTAMP.value,
        start_hour=6,
    ).merge()

    mideo_converter.BatchVideoRender(
        input_folder_path=merged_dir,
        output_folder_path=target_path / "cut_silence",
        valid_extensions=set(mideo_converter.VideoSuffix),
        walkthrough=False,
        post_hook=mideo_converter.PostHooks.set_epoch_timestamp(
            datetime_pattern=mideo_converter.RE_PATTERN.EPOCHSTAMP.value
        ),
    ).apply(
        task=mideo_converter.ffmpeg_toolkit.PARTIAL_TASKS.cut_silence(
            dB=-15, delete_after=False
        )
    )


if __name__ == "__main__":
    main()
