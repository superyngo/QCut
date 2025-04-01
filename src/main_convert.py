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
        timestamp_pattern=mideo_converter.RE_PATTERN.EPOCHSTAMP.value,
    ).merge()

    mideo_converter.BatchVideoRender(
        input_folder_path=target_path,
        output_folder_path=target_path / "cl",
        valid_extensions={mideo_converter.VideoSuffix.MKV},
        walkthrough=False,
        delete_after=False,
        post_hook=mideo_converter.PostHooks.set_epoch_timestamp(
            timestamp_pattern=mideo_converter.RE_PATTERN.EPOCHSTAMP.value
        ),
    ).apply(
        task=mideo_converter.PARTIAL_TASKS.cut_motionless_rerender(threshold=0.0095),
    )


if __name__ == "__main__":
    main()
