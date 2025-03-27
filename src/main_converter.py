from app import mideo_converter
from pathlib import Path


def main() -> None:
    target_path: Path = Path(r"F:\Users\user\Downloads")
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
        output_folder_path=target_path / "partitioned",
        valid_extensions={mideo_converter.VideoSuffix.MKV},
        walkthrough=False,
        delete_after=False,
        post_hook=mideo_converter.PostHooks.set_epoch_timestamp(
            timestamp_pattern=mideo_converter.RE_PATTERN.EPOCHSTAMP.value
        ),
    ).apply(
        task=mideo_converter.ffmpeg_toolkit.PARTIAL_TASKS.partion_video(
            output_dir=target_path / "partitioned",
            partition_config=mideo_converter.ffmpeg_toolkit.PartitionConfig(
                portion_method=[
                    (1, mideo_converter.ffmpeg_toolkit.PARTIAL_TASKS.speedup()),
                    (2, mideo_converter.ffmpeg_toolkit.PARTIAL_TASKS.cut_silence()),
                    (3, mideo_converter.ffmpeg_toolkit.PARTIAL_TASKS.cut_motionless()),
                    (4, mideo_converter.ffmpeg_toolkit.PARTIAL_TASKS.jumpcut()),
                    (
                        5,
                        mideo_converter.ffmpeg_toolkit.PARTIAL_TASKS.partion_video(
                            output_dir=target_path / "partitioned4",
                            partition_config=mideo_converter.ffmpeg_toolkit.PartitionConfig(
                                portion_method=[
                                    (
                                        1,
                                        mideo_converter.ffmpeg_toolkit.PARTIAL_TASKS.speedup(),
                                    ),
                                    (
                                        2,
                                        mideo_converter.ffmpeg_toolkit.PARTIAL_TASKS.cut_silence(),
                                    ),
                                    (
                                        3,
                                        mideo_converter.ffmpeg_toolkit.PARTIAL_TASKS.cut_motionless(),
                                    ),
                                    (
                                        4,
                                        mideo_converter.ffmpeg_toolkit.PARTIAL_TASKS.jumpcut(),
                                    ),
                                    (
                                        5,
                                        mideo_converter.ffmpeg_toolkit.PARTIAL_TASKS.partion_video(
                                            output_dir=target_path / "partitioned44",
                                        ),
                                    ),
                                ]
                            ),
                        ),
                    ),
                ]
            ),
        )
    )


if __name__ == "__main__":
    main()
