import os
import re
from datetime import datetime, timedelta, date
from enum import Enum
from pathlib import Path
from pydantic import BaseModel, computed_field, Field
from app.common import logger
from app.services import ffmpeg_toolkit
from typing import Callable

VideoSuffix = ffmpeg_toolkit.types.VideoSuffix
FunctionEnum = ffmpeg_toolkit.types.FunctionEnum


class RE_PATTERN(Enum):
    EPOCHSTAMP = re.compile(r"(?<!\d)\d{10}(?!\d)")
    DATETIMESTAMP = re.compile(r"(?<!\d)\d{14}(?!\d)")  # YYYYMMDDHHMMSS


type ValidExtensions = set[VideoSuffix] | set[str] | None


def _list_video_files(
    root_path: str | Path,
    valid_extensions: ValidExtensions,
    walkthrough: bool = True,
) -> list[Path]:
    if valid_extensions is None:
        valid_extensions = set(VideoSuffix)

    root_path = Path(root_path)
    video_files: list[Path] = []

    # Use rglob to recursively find files with the specified extensions
    video_files = (
        [
            file
            for file in root_path.rglob("*")
            if file.is_file() and file.suffix.lstrip(".").lower() in valid_extensions
        ]
        if walkthrough
        else [
            file
            for file in root_path.iterdir()
            if file.is_file() and file.suffix.lstrip(".").lower() in valid_extensions
        ]
    )

    return video_files


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
    datetime_pattern: re.Pattern, video_files: list[Path], start_hour: int = 0
) -> GroupedVideos:
    grouped_files: GroupedVideos = {}

    for video in video_files:
        epoch_time: int | None = _extract_pattern(str(video.stem), datetime_pattern)

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
            ffmpeg_toolkit.FFRenderTasks().merge(
                input_dir_or_files=input_files,
                output_file=output_file,
                output_kwargs=output_kwargs,
            ).render()

            os.utime(output_file, (first_video_epoch, first_video_epoch))

            logger.info(
                f"Processed {date_key}, saved to {output_file}, set timestamps to {first_video_epoch}."
            )

        except Exception as e:
            logger.error(f"Failed to concatenate videos for {date_key}. Error: {e}")
            return 1
    return 0


class PostHooks(FunctionEnum):
    @staticmethod
    def set_epoch_timestamp(datetime_pattern: re.Pattern):
        def _set_epoch_timestamp(_video: Path, output_file: Path):
            """Set the epoch timestamp of the video file."""
            epoch_time: int | None = _extract_pattern(
                str(output_file.stem), datetime_pattern
            )

            # Check if epoch_time is a valid epoch timestamp or a datestamp
            if len(str(epoch_time)) == 14:
                epoch_time = _convert_datestamp_to_epoch(str(epoch_time))

            if not epoch_time:
                logger.warning(f"skip {output_file} with no time to judge.")
                return

            os.utime(output_file, (epoch_time, epoch_time))

        return _set_epoch_timestamp


class BatchVideoRender(BaseModel):
    """Video merger configuration and processor.

    Handles merging of video files in a folder based on their date.
    """

    input_folder_path: Path
    output_folder_path: Path | None = None
    valid_extensions: ValidExtensions = None
    walkthrough: bool = False
    input_kwargs: ffmpeg_toolkit.types.FFKwargs = Field(default_factory=dict)
    output_kwargs: ffmpeg_toolkit.types.FFKwargs = Field(default_factory=dict)
    delete_after: bool = False
    post_hook: Callable | None = None

    def model_post_init(self, *args, **kwargs):
        if self.output_folder_path is None:
            self.output_folder_path = self.input_folder_path
        if self.output_folder_path.suffix == "" and self.output_folder_path.is_file():
            raise ValueError("Output folder path is a file.")
        self.output_folder_path.mkdir(parents=True, exist_ok=True)
        if self.valid_extensions is None:
            self.valid_extensions = set(VideoSuffix)

    @computed_field
    @property
    def video_files(self) -> list[Path]:
        """List all video files in the specified folder with valid extensions."""
        files = _list_video_files(
            self.input_folder_path,
            valid_extensions=self.valid_extensions,
            walkthrough=self.walkthrough,
        )
        logger.info(f"Found {len(files)} video files in {self.input_folder_path}")
        return files

    def apply(self, task: Callable):
        """Batch Render the video files."""
        for video in self.video_files:
            output_gile = task(
                input_file=video,
                output_file=self.output_folder_path,
                options={"delete_after": self.delete_after},
            )
            if self.post_hook:
                logger.info("Post hooking...")
                self.post_hook(video, output_gile)


class MergeByDate(BatchVideoRender):
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
