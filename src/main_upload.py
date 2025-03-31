import os
import asyncio
from pathlib import Path
from pydantic.networks import AnyUrl
from app import gp_uploader, logger, constants

os.environ["HTTPS_PROXY"] = ""
os.environ["HTTP_PROXY"] = ""

edge_path = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
driver_config: gp_uploader.types.DriverConfig = {
    "user_data_dir": Path(constants.APP_PATHS.APP_DATA) / "config",
    "browser_executable_path": edge_path,
}

uploader_config_1: gp_uploader.types.GPUploaderConfig = {
    "name": "Mom",
    "local_album_path": Path(r"F:\NoCloud\c"),
    "GPhoto_url": AnyUrl(
        "https://photos.google.com/share/AF1QipOjEaSgW_YJxNembwfgYQbouBBHSUyQxFGj2Oq6dpw_EjkWeCBRkSRwczoP7WwoUw"
    ),
    "delete_after": True,
}
uploader_config_2: gp_uploader.types.GPUploaderConfig = {
    "name": "Mom_speedup",
    "local_album_path": Path(r"D:\smb\xiaomi\xiaomi_camera_videos\94f827b4b94e")
    / "cut_sl_speedup",
    "GPhoto_url": AnyUrl(
        "https://photos.google.com/share/AF1QipNG24NndfSGD9rsiHkz7OBvA5amkVOxcadMFI52a0HZR3m9wlUwTgOn5b2h7YBA2Q"
    ),
    "delete_after": True,
}
uploader1 = gp_uploader.Uploader(
    driver_config=driver_config, uploader_config=uploader_config_1
)
uploader2 = gp_uploader.Uploader(
    driver_config=driver_config, uploader_config=uploader_config_2
)
upload_assignments: gp_uploader.types.Assignments = {
    "filename": Path(),
    "assignments": [uploader1, uploader2],
}


async def main():
    assignments = upload_assignments.get("assignments", [])
    if not assignments:
        logger.info("No assignment")
        return
    logger.info(f"Start uploading: {upload_assignments}")
    for uploader in assignments:
        if not uploader.mkv_files:
            logger.info(
                f"No mkv files in {uploader.uploader_config.get('local_album_path')}, pass"
            )
            return
        await uploader.init()

        await uploader.upload()

    # Clear tabs
    logger.info("All uploads done, close all browsers")

    for uploader in assignments:
        if uploader.browser is None:
            continue
        if uploader.browser.stopped:
            continue
        uploader.browser.stop()
        del uploader


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
