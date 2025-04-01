import time
from nodriver import Tab, Browser
import nodriver as nd
from pathlib import Path
from nodriver.cdp import network
from pydantic import BaseModel, computed_field, field_validator
from weakref import WeakValueDictionary
from typing import Self
from ...utils import composer

try:
    from app.common import logger  # type: ignore
except ImportError:
    # Fallback to a default value
    class logger:
        @classmethod
        def info(cls, message: str) -> None:
            print(message)

        @classmethod
        def error(cls, message: str) -> None:
            print(message)


# Multiton state
type BrowserInstances = WeakValueDictionary[str, Browser]
_driver_instances: BrowserInstances = WeakValueDictionary()

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

    global _driver_instances

    browser: Browser | None = None
    tab: Tab | None = None
    driver_instances: BrowserInstances = _driver_instances
    user_data_dir: Path | None = None
    browser_executable_path: Path | None = None

    @field_validator("user_data_dir")
    def validate_user_data_dir(cls, value: Path) -> Path:
        if value.is_file():
            raise ValueError(f"The path '{value}' is a file.")
        return value

    @field_validator("browser_executable_path")
    def validate_browser_executable_path(cls, value: Path) -> Path:
        if not value.exists():
            raise ValueError(f"The path '{value}' does not exist.")
        if not value.is_file():
            raise ValueError(f"The path '{value}' is not a file.")
        return value

    @computed_field
    @property
    def driver_id(self) -> str:
        """Get the browser id."""
        return str(self.user_data_dir) + str(self.browser_executable_path)

    class Config:
        arbitrary_types_allowed = True

    async def init(self) -> Self:
        """Ensure driver is initialized."""
        # Initialize or reuse the browser instance
        if (
            self.driver_id in _driver_instances.keys()
            and not _driver_instances[self.driver_id].stopped
        ):
            logger.info(
                f"Reusing existing browser instance {_driver_instances[self.driver_id]}"
            )
            self.browser = _driver_instances[self.driver_id]
            self.tab = self.browser.tabs[0]

        else:
            logger.info(
                f"Initialyze browser instance with user data in {self.user_data_dir} and {self.browser_executable_path}"
            )
            self.browser = await nd.start(
                user_data_dir=self.user_data_dir,
                browser_executable_path=self.browser_executable_path,
            )
            _driver_instances[self.driver_id] = self.browser
            # Initialize the tab
            self.tab = await self.browser.get("about:blank")
            composer.compose(self.tab, {"get_response": get_response})

        self.driver_instances = _driver_instances

        return self


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
