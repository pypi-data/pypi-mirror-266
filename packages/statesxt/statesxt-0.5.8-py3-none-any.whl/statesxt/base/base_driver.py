from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.service import Service as BraveService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.core.os_manager import ChromeType
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
import logging
import time
import sys

from .mouse_keys import MouseKeysDriver
from .check import CheckDriver
from .table import TableDriver
from .form import FormDriver
from .wait import WaitDriver


class BaseDriver:
    """Wraps driver and provides all common-used WebDriver actions"""

    def __init__(self, browser, domain=None, fullscreen=True, duration: int = 10) -> None:
        self.setup(browser, domain, fullscreen)

        self.cd = CheckDriver(self.__driver, duration)
        self.fd = FormDriver(self.__driver, duration)
        self.mkd = MouseKeysDriver(self.__driver)
        self.td = TableDriver(self.__driver, duration)
        self.wd = WaitDriver(self.__driver, duration)

    def setup(self, browser, domain, fullscreen) -> None:
        """Sets up which browser and domain to use"""

        try:
            # setup driver
            print("\nSetting up driver...", end=" ")
            start = time.time()
            if browser == "brave":
                self.__driver = webdriver.Chrome(service=BraveService(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()))
            elif browser == "chrome":
                self.__driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
            elif browser == "edge":
                self.__driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
            elif browser == "firefox":
                self.__driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
            end = time.time()
            print(f"Takes {end-start} seconds to complete.")

            # setup domain
            print("\nSetting up domain...", end=" ")
            start = time.time()
            if domain:
                self.__driver.get("<Your Custom Domain URL>")
            else:
                self.__driver.get("<Your URL>")
            end = time.time()
            print(f"Takes {end-start} seconds to complete.")

            # setup screen size
            if fullscreen:
                self.__driver.maximize_window()
        except Exception as e:
            logging.getLogger(f"root.{__name__}.{self.__class__.__name__}.{sys._getframe().f_code.co_name}").error(f"in the process of running setup:\n{str(e)}")
            raise Exception(str(e))

    def close_tab(self) -> None:
        """Closes the current tab, and backs to the initial tab"""

        self.__driver.close()
        self.focus_to(0)

    def exit(self) -> None:
        self.__driver.quit()

    def focus_to(self, index: int = -1) -> None:
        """Changes the focus of the driver"""

        self.__driver.switch_to.window(self.__driver.window_handles[index])

    def go_to(self, href: str):
        self.__driver.get(href)

    def navigate(self, url: str) -> None:
        """Loads a web page in the current browser session"""

        self.__driver.get(url)
        self.focus_to()

    def refresh(self) -> None:
        """Refreshes the browser"""

        self.__driver.refresh()
