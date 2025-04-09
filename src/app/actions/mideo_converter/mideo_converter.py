import os
import re
import ffmpeg_toolkit
from datetime import datetime, timedelta, date
from enum import Enum
from pathlib import Path
from pydantic import computed_field, Field
from app.common import logger

VideoSuffix = ffmpeg_toolkit.types.VideoSuffix
FunctionEnum = ffmpeg_toolkit.types.FunctionEnum
PARTIAL_TASKS = ffmpeg_toolkit.PARTIAL_TASKS

BatchTask = ffmpeg_toolkit.BatchTask


class RE_PATTERN(Enum):
    EPOCHSTAMP = re.compile(r"(?<!\d)\d{10}(?!\d)")
    DATETIMESTAMP = re.compile(r"(?<!\d)\d{14}(?!\d)")  # YYYYMMDDHHMMSS


type ValidExtensions = set[ffmpeg_toolkit.types.VideoSuffix] | set[str] | None


def _extract_pattern(text: str, pattern: re.Pattern) -> int | None:
    """Function to extract text using regex"""

    try:
        matches = pattern.findall(text)
        if matches:
            logger.info(f"Found matches {matches[0]} in {text} with {pattern}")
            return int(matches[0])
        else:
            logger.warning(f"No mathces found in {text} with {pattern}")
            return None
    except ValueError as e:
        logger.error(f"Failed to extract pattern from {text}: {str(e)}")
        return None


def _convert_datestamp_to_epoch(datestamp: str) -> int:
    """Convert a datestamp in the format YYYYMMDDHHMMSS to epoch time."""
    try:
        dt = datetime.strptime(datestamp, "%Y%m%d%H%M%S")
        return int(dt.timestamp())
    except ValueError as e:
        logger.error(f"Failed to convert datestamp {datestamp} to epoch: {str(e)}")
        raise (e)


type GroupedVideos = dict[date, dict[int, Path]]


def _group_files_by_date(
    timestamp_pattern: re.Pattern, video_files: list[Path], start_hour: int = 0
) -> GroupedVideos:
    grouped_files: GroupedVideos = {}

    for video in video_files:
        epoch_time: int | None = _extract_pattern(str(video.stem), timestamp_pattern)

        # Check if epoch_time is a valid epoch timestamp or a datestamp
        if len(str(epoch_time)) == 14:
            epoch_time = _convert_datestamp_to_epoch(str(epoch_time))

        if epoch_time is None:
            logger.warning(f"skip {video} with no time.")
            continue

        else:
            file_datetime: datetime = datetime.fromtimestamp(epoch_time)
            if file_datetime.hour < start_hour:
                file_datetime -= timedelta(days=1)
            date_key: date = file_datetime.date()

        if date_key not in grouped_files:
            grouped_files[date_key] = {}

        grouped_files[date_key].update({epoch_time: video})

    return grouped_files


def _merge_videos(
    video_dict: GroupedVideos,
    save_path: Path,
    output_kwargs: ffmpeg_toolkit.types.FFKwargs,
) -> int:
    today: date = datetime.today().date()

    for date_key, videos in video_dict.items():
        if date_key == today:
            logger.info(f"Skipping today's date: {date_key}")
            continue

        # Sort the videos by epoch time
        sorted_videos = dict(sorted(videos.items()))

        # Prepare the input file list with valid check for ffmpeg
        input_files: list[Path] = []
        for video_path in sorted_videos.values():
            if ffmpeg_toolkit.FPRenderTasks().is_valid_video(video_path):
                input_files.append(video_path)

        if not input_files:
            logger.info(f"No valid videos found for {date_key}. Skipping.")
            continue

        # Get the file's timestamp to the first video's epoch time
        first_video_epoch = next(iter(sorted_videos))

        # Define the output file path
        output_file: Path = save_path / f"{date_key}_{first_video_epoch}_merged.mkv"
        logger.info(f"{output_file = }")
        try:
            # Use ffmpeg to concatenate videos
            ffmpeg_toolkit.Merge(
                input_dir_or_files=input_files,
                output_file=output_file,
                output_kwargs=output_kwargs,
            ).render()

            os.utime(output_file, (first_video_epoch, first_video_epoch))

            logger.info(
                f"Merged {date_key} video, saved to {output_file}, set timestamps to {first_video_epoch}."
            )

        except Exception as e:
            logger.error(f"Failed to concatenate videos for {date_key}. Error: {e}")
            return 1
    return 0


class PostHooks(FunctionEnum):
    @staticmethod
    def set_epoch_timestamp(timestamp_pattern: re.Pattern):
        def _set_epoch_timestamp(_video: Path, output_file: Path):
            """Set the epoch timestamp of the video file."""
            epoch_time: int | None = _extract_pattern(
                str(output_file.stem), timestamp_pattern
            )

            # Check if epoch_time is a valid epoch timestamp or a datestamp
            if len(str(epoch_time)) == 14:
                epoch_time = _convert_datestamp_to_epoch(str(epoch_time))

            if not epoch_time:
                logger.warning(f"skip {output_file} with no time to judge.")
                return

            os.utime(output_file, (epoch_time, epoch_time))

        return _set_epoch_timestamp


class MergeByDate(BatchTask):
    """Video merger configuration and processor."""

    start_hour: int = Field(
        default=6, ge=0, le=23, description="Hour to use as day boundary (0-23)"
    )
    timestamp_pattern: re.Pattern

    @computed_field
    @property
    def videos_grouped_by_date(self) -> GroupedVideos:
        """Group video files by date based on the start hour."""
        if len(self.video_files) == 0:
            logger.info("No video files to be merged by date")
            return {}
        return _group_files_by_date(
            self.timestamp_pattern,
            self.video_files,
            self.start_hour,
        )

    def merge(self) -> int:
        """Process the video merging operation.

        Returns:
            int: Status code (0 for success, other values for errors)
        """
        logger.info(f"Start merging videos in {self.input_folder_path}")

        if not self.video_files:
            logger.info(f"No {self.valid_extensions} files in {self.input_folder_path}")
            return 1

        try:
            do: int = _merge_videos(
                self.videos_grouped_by_date,
                self.output_folder_path or self.input_folder_path,
                self.output_kwargs,
            )

            # Clean up original video directories
            if self.delete_after:
                dirs_to_delete: set[Path] = set()
                for videos in self.videos_grouped_by_date.values():
                    for video in videos.values():
                        logger.info(f"Delete source video {video}.")
                        os.remove(video)
                        dirs_to_delete.add(video.parent)
                for directory in dirs_to_delete:
                    if list(directory.iterdir()) == []:
                        logger.info(f"Delete source videos dir {directory}.")
                        os.rmdir(directory)

        except OSError as e:
            logger.error(f"Failed to delete files or directories with {e}")
            return 2

        return do


def main() -> None:
    pass


if __name__ == "__main__":
    main()


# def get_speedup_range(start_hour: int, end_hour: int) -> range | list[int]:
#     # Create the speedup range, handling wrap-around at midnight
#     if end_hour >= start_hour:
#         return range(start_hour, end_hour + 1)
#     else:
#         return list(range(start_hour, 25)) + list(range(0, end_hour + 1))
