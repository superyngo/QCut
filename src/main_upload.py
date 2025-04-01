import os
import asyncio
from pathlib import Path
from pydantic import AnyUrl
from app import gp_uploader, logger, constants

# Fix for "RuntimeError: Event loop is closed" on Windows
# if os.name == "nt":  # Check if the OS is Windows
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

MyDriverConfig = gp_uploader.types.MyDriverConfig
UploaderConfig = gp_uploader.types.UploaderConfig

os.environ["HTTPS_PROXY"] = ""
os.environ["HTTP_PROXY"] = ""

edge_path = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
local_dir = Path(r"F:\Users\user\Downloads")
driver_config: MyDriverConfig = {
    "user_data_dir": Path(constants.APP_PATHS.APP_DATA / "config"),
    "browser_executable_path": edge_path,
}

uploader1 = gp_uploader.Uploader(
    **driver_config,
    task_name="Mom",
    local_album_path=local_dir,
    GPhoto_url=AnyUrl(
        "https://photos.google.com/share/AF1QipOjEaSgW_YJxNembwfgYQbouBBHSUyQxFGj2Oq6dpw_EjkWeCBRkSRwczoP7WwoUw"
    ),
    delete_after=False,
)

uploader2 = gp_uploader.Uploader(
    **driver_config,
    task_name="Mom_speedup",
    local_album_path=local_dir / "cl",
    GPhoto_url=AnyUrl(
        "https://photos.google.com/share/AF1QipNG24NndfSGD9rsiHkz7OBvA5amkVOxcadMFI52a0HZR3m9wlUwTgOn5b2h7YBA2Q"
    ),
    delete_after=False,
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
    logger.info(
        f"Start uploading tasks: {[assignment.task_name for assignment in upload_assignments['assignments']]}"
    )
    for index, uploader in enumerate(assignments):
        await uploader.init()

        if uploader.mkv_files:
            logger.info(
                f"Start uploading {uploader.task_name} to {uploader.GPhoto_url}"
            )
            await uploader.upload()
        else:
            logger.info(f"No mkv files in {uploader.local_album_path}, pass")

        # Close tab for the last uploader
        if index == len(assignments) - 1:
            logger.info(f"All tasks finished, closing tab for {uploader.task_name}")
            await uploader.tab.close()  # type:ignore


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    task = loop.create_task(main())
    loop.run_until_complete(task)
    pending = asyncio.all_tasks(loop=loop)
    group = asyncio.gather(*pending)

    loop.close()
