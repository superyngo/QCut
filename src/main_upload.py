import os
import asyncio
from pathlib import Path
from pydantic.networks import AnyUrl
from app import GPUploader, logger, constants

os.environ["HTTPS_PROXY"] = ""
os.environ["HTTP_PROXY"] = ""

edge_path = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
driver_config: GPUploader.DriverConfig = {
    "user_data_dir": Path(constants.APP_PATHS.APP_DATA) / "config",
    "browser_executable_path": edge_path,
}

task1: GPUploader.GPUploaderTask = {
    "name": "Mom",
    "local_album_path": Path(r"F:\NoCloud\c"),
    "GPhoto_url": AnyUrl(
        "https://photos.google.com/share/AF1QipOjEaSgW_YJxNembwfgYQbouBBHSUyQxFGj2Oq6dpw_EjkWeCBRkSRwczoP7WwoUw"
    ),
    "delete_after": True,
}

task2: GPUploader.GPUploaderTask = {
    "name": "Mom_speedup",
    "local_album_path": Path(r"D:\smb\xiaomi\xiaomi_camera_videos\94f827b4b94e")
    / "cut_sl_speedup",
    "GPhoto_url": AnyUrl(
        "https://photos.google.com/share/AF1QipNG24NndfSGD9rsiHkz7OBvA5amkVOxcadMFI52a0HZR3m9wlUwTgOn5b2h7YBA2Q"
    ),
    "delete_after": True,
}


upload_assignments: GPUploader.Assignments = {
    "filename": Path(),
    "assignments": [task1, task2],
}

logger.info(f"Start uploading tasks:{upload_assignments}")


async def main():
    driver = GPUploader(driver_config=driver_config)
    await driver.init()

    if not upload_assignments:
        logger.info("No assignment")
        return

    for task in assignments:
        folder: Path = task["local_album_path"]
        task["mkv_files"] = mkv_files = [
            folder / file for file in os.listdir(folder) if file.endswith(".mkv")
        ]

        if not mkv_files:
            logger.info(f"No mkv files in {folder}, pass")
            return

        logger.info(f"Start uploading {mkv_files} to {task['GPhoto_url']}")
        await GPhoto_uploader.upload_handler(task)

    # Clear tabs
    logger.info(f"All tasks done, close all browsers")
    keys = list(browser_instances.keys())
    for key in keys:
        if key in browser_instances:
            browser_instances[key].stop()
            del browser_instances[key]

    # Your script code here
    # print("This is a script in debug mode.")
    # Set a breakpoint
    # pdb.set_trace()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
