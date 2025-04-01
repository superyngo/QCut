import asyncio
import os
from pydantic import computed_field, AnyUrl, field_validator
from pathlib import Path
from app.common import logger
from ...services import my_driver
from ffmpeg_toolkit import types as ffmpeg_types


class Uploader(my_driver.MyDriver):
    """_summary_

    Args:
       task: GPUploaderTask | None = None

    Returns:
        _type_: _description_
    """

    task_name: str
    local_album_path: Path
    GPhoto_url: AnyUrl
    valid_extensions: set[ffmpeg_types.VideoSuffix] = {ffmpeg_types.VideoSuffix.MKV}
    delete_after: bool = True

    @field_validator("local_album_path")
    def validate_local_album_path(cls, value):
        if not value.exists() or not value.is_dir():
            raise ValueError(
                f"The path '{value}' does not exist or is not a directory."
            )
        return value

    @computed_field
    @property
    def mkv_files(self) -> list[Path]:
        mkv_files: list[Path] = [
            file
            for file in self.local_album_path.iterdir()
            if file.suffix.lstrip(".") in self.valid_extensions
        ]

        if not mkv_files:
            logger.warning("No valid files found")
            return []

        return mkv_files

    async def upload(self) -> int:
        if self.tab is None:
            logger.warning("Tab not initialized")
            return 1

        if self.mkv_files == []:
            logger.warning("No mkv file")
            return 1

        await self.tab.get(str(self.GPhoto_url))
        # Locate the 新增相片 and click
        Add_New = await self.tab.find("//span[text()='新增相片']", timeout=999)
        if not Add_New:
            logger.warning("新增相片 not found")
            return 2
        await Add_New.click()
        logger.info("新增相片")

        # Interact with the "Select from Computer" button
        upload_button = await self.tab.find('//span[text()="從電腦中選取"]')
        if not upload_button:
            logger.info("從電腦中選取 not found")
            return 2
        await self.tab.evaluate(
            """
            document.addEventListener('click', (event) => {
            if (event.target.type === 'file') {
                event.preventDefault(); // Prevent file dialog
                console.log('File dialog prevented');
            }
            });
        """
        )
        await upload_button.click()
        logger.info("從電腦中選取")

        # Locate the file input element
        file_input = await self.tab.find('//input[@type="file"]')
        if not file_input:
            logger.info("upload not found")
            return 2
        await file_input.send_file(*self.mkv_files)  # Set files for upload

        # Wait for confirmation message
        await self.tab.find("你已備份", timeout=999999999)
        logger.info("上傳成功，等待5秒後續動作")

        await self.tab.wait(5)

        # Delete the .mkv files if specified
        if self.delete_after:
            _delete_mkv_files(self.mkv_files)

        return 0


def _delete_mkv_files(mkv_files: list[Path]) -> int:
    # Iterate through each .mkv file and delete it
    try:
        for file in mkv_files:
            os.remove(file)
            logger.info(f"Deleted: {file}")
        return 0

    except Exception as e:
        logger.info(f"Error deleting {mkv_files}: {e}")
        return 1


async def main():
    pass


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
