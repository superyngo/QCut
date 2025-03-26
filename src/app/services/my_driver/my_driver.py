import time
from nodriver import Tab, Browser
import nodriver as nd
from nodriver.cdp import network
from pathlib import Path
from pydantic import BaseModel, field_validator
from weakref import WeakValueDictionary
from typing import Self, Any
from ...utils import composer


# Multiton state
type BrowserInstances = WeakValueDictionary[str, Browser]
driver_instances: BrowserInstances = WeakValueDictionary()

# Create a WeakValueDictionary
response_codes: WeakValueDictionary[str, int] = WeakValueDictionary()


async def get_response(tab: Tab, url: str) -> int:
    await tab.send(network.enable())

    global response_codes
    # Add a handler for ResponseReceived events
    tab.add_handler(
        network.ResponseReceived,
        lambda e: (
            response_codes.update({e.response.url: e.response.status})
            if e.response.url == url
            else None
        ),
    )
    await tab.get(url)

    while response_codes.get(url) is None:
        time.sleep(1)

    await tab.send(network.disable())
    return response_codes[url]


class MyDriver(BaseModel):
    """_summary_

        Args:
            user_data_dir (Path | None, optional): _description_. Defaults to None.
            browser_executable_path (Path | None, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """

    user_data_dir: Path | None = None
    browser_executable_path: Path | None = None
    browser: Browser | None = None
    tab: Tab | None = None
    driver_instances: BrowserInstances = driver_instances
    init: Any

    class Config:
        arbitrary_types_allowed = True

    @field_validator("init")
    @classmethod
    async def init_driver(cls, init, self):
        """Ensure driver is initialized."""
        global driver_instances
        driver_id: str = str(self.user_data_dir) + str(self.browser_executable_path)

        # Initialize or reuse the browser instance
        if driver_id in driver_instances and not driver_instances[driver_id].stopped:
            self.browser = driver_instances[driver_id]
        else:
            self.browser = await nd.start(
                user_data_dir=self.user_data_dir,
                browser_executable_path=self.browser_executable_path,
            )
            self.driver_instances[driver_id] = self.browser

        # Initialize the tab
        self.tab = await self.browser.get("about:blank")
        composer.compose(self.tab, {"get_response": get_response})


# Restrart not working yet
# async def _restart(browser: Browser) -> None:
#     await self.stop()
#     browser_config = {
#         k: v
#         for (k, v) in self.config.__dict__.items()
#         if k in ["user_data_dir", "browser_executable_path"]
#     }
#     driver_id: Path = browser_config.get("user_data_dir", Path())
#     driver_instances[driver_id] = await nd.start(**browser_config)
#     self = driver_instances[driver_id]
