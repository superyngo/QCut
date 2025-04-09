from app import mideo_converter, constants


def main() -> None:
    mideo_converter.MergeByDate(
        input_folder_path=constants.CONFIG.TARGET_PATH.value,
        valid_extensions={mideo_converter.VideoSuffix.MP4},
        walkthrough=True,
        delete_after=True,
        start_hour=6,
        timestamp_pattern=mideo_converter.RE_PATTERN.EPOCHSTAMP.value,
    ).merge()

    mideo_converter.BatchTask(
        input_folder_path=constants.CONFIG.TARGET_PATH.value,
        output_folder_path=constants.CONFIG.RENDERED_FOLDER_PATH.value,
        valid_extensions={mideo_converter.VideoSuffix.MKV},
        walkthrough=False,
        delete_after=False,
        post_hook=mideo_converter.PostHooks.set_epoch_timestamp(
            timestamp_pattern=mideo_converter.RE_PATTERN.EPOCHSTAMP.value
        ),
    ).render(
        task=mideo_converter.PARTIAL_TASKS.cut_silence(dB=-15),
    )


if __name__ == "__main__":
    main()
