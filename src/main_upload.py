import os
import asyncio
from pathlib import Path
from app import GPhoto_uploader, browser_instances, logger
from app.services.my_driver.types import MyDriverConfig
from app.services.my_driver import MyBrowser

os.environ["HTTPS_PROXY"] = ""
os.environ["HTTP_PROXY"] = ""

b = MyBrowser(
    browser_executable_path=Path(
        r"C:\Program Files (x86)\Microsoft\EdgeCore\134.0.3124.83\msedge.exe"
    )
)
await b.browser

# sample
name = "abc"
browser_config: MyDriverConfig = {
    "user_data_dir": Path(config.AppPaths.APP_DATA) / name,
    "browser_executable_path": Path(
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    ),
}

task1: tasks.UploaderTask = {
    "name": "Mom",
    "local_album_path": Path(r"F:\NoCloud\c"),
    "GPhoto_url": "https://photos.google.com/share/AF1QipOjEaSgW_YJxNembwfgYQbouBBHSUyQxFGj2Oq6dpw_EjkWeCBRkSRwczoP7WwoUw",
    "browser_config": browser_config,
    "delete_after": True,
}
task2: tasks.UploaderTask = {
    "name": "Mom_speedup",
    "local_album_path": Path(r"D:\smb\xiaomi\xiaomi_camera_videos\94f827b4b94e")
    / "cut_sl_speedup",
    "GPhoto_url": "https://photos.google.com/share/AF1QipNG24NndfSGD9rsiHkz7OBvA5amkVOxcadMFI52a0HZR3m9wlUwTgOn5b2h7YBA2Q",
    "browser_config": browser_config,
    "delete_after": True,
}

upload_assignments: tasks.UploaderInfo = {
    "filename": Path(),
    "assignments": [task1, task2],
}


async def main():
    assignments = upload_assignments.get("assignments")
    logger.info(f"Start uploading tasks:{assignments}")

    if not assignments:
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
