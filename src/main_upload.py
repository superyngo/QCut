import os
from weakref import WeakKeyDictionary
import nodriver as uc
from pathlib import Path
from app import gp_uploader, logger, constants

# Fix for "RuntimeError: Event loop is closed" on Windows
# if os.name == "nt":  # Check if the OS is Windows
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

MyDriverConfig = gp_uploader.types.MyDriverConfig
UploaderConfig = gp_uploader.types.UploaderConfig

os.environ["HTTPS_PROXY"] = ""
os.environ["HTTP_PROXY"] = ""

driver_config: MyDriverConfig = {
    "user_data_dir": constants.CONFIG.BROWSER_CONFIG_FOLDER_NAME.value,
    "browser_executable_path": constants.CONFIG.EDGE_PATH.value,
}

uploader1 = gp_uploader.Uploader(
    **driver_config,
    task_name="Mom",
    local_album_path=constants.CONFIG.TARGET_PATH.value,
    GPhoto_url=constants.ALBUMS_URL.MOM.value,
    delete_after=True,
)

uploader2 = gp_uploader.Uploader(
    **driver_config,
    task_name="Mom_speedup",
    local_album_path=constants.CONFIG.RENDERED_FOLDER_PATH.value,
    GPhoto_url=constants.ALBUMS_URL.MOM_SPEEDUP.value,
    delete_after=True,
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

    driver_instances: gp_uploader.types.BrowserInstances | WeakKeyDictionary = (
        WeakKeyDictionary()
    )
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

        # Close tab at the last uploader finished
        if index == len(assignments) - 1:
            logger.info(f"All tasks finished, closing tab for {uploader.task_name}")
            driver_instances = uploader.driver_instances

        del uploader

        for driver in driver_instances.values():
            driver.stop()  # type:ignore


if __name__ == "__main__":
    uc.loop().run_until_complete(main())
