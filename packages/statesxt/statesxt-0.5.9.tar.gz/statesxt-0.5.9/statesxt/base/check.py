from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.edge.webdriver import WebDriver
from selenium.webdriver.common.by import By
import time

from .mouse_keys import MouseKeysDriver
from .wait import WaitDriver


class CheckDriver:
    def __init__(self, driver: WebDriver, duration: int) -> None:
        self.wd = WaitDriver(driver, duration)
        self.mkd = MouseKeysDriver(driver)
        self.__driver = driver

    def check_alert(self, isSuccess: bool, isVisible: bool, cust_message: str = None) -> bool:
        """
        Checks the presence of alert element

        Args:
            isSuccess (bool): tyoe of the alert, e.g. True means the alert is expected to be a 'success' type of alert
            isVisible (bool): alert condition, e.g. True means the alert is expected to be visible
            cust_message (str): is a custom message, which other than both 'success' and 'fail'

        Returns:
            bool: True means that the element is found, and vice versa
        """

        if isVisible:
            alert = self.wd.an_element(By.CLASS_NAME, "toast-body")
            if isSuccess:
                if alert.text == "success" or alert.text == cust_message:
                    return True
            else:
                if alert.text == "fail" or alert.text == cust_message:
                    return True
            return False
        else:
            alert = self.wd.invisible(By.CLASS_NAME, "toast-body")
            return True if alert else False

    def check_indicator_row(
        self,
        available_rows: list[WebElement],
        target_row: list,
    ) -> bool:
        """
        Checks whether an indicator row is listed or not

        Args:
            available_rows (list[WebElement]): contains all row elements
            target_row (list): contains the data to be compared

        Returns:
            bool: True means the result has met the expectation, and vice versa
        """

        def get_data_of_a_row(row: WebElement):
            tds = row.find_elements(By.TAG_NAME, "td")
            return [tds[i].text for i in range(4)]  # 4 are name, indicator, logic, and threshold value

        for row in available_rows:
            self.mkd.scrolling(element=row)

            rowdata = get_data_of_a_row(row)
            # check the current row
            if rowdata == target_row:
                return True
        return False

    def check_viewport(self, target_element: WebElement) -> bool:
        """
        Checks if an element is within the current viewport

        Args:
            target_element (WebElement): is the element whose position will be checked againts the viewport

        Returns:
            bool: True means that the element is within the viewport, and vice versa
        """

        if target_element:
            # since there are cases where the element is in progress to get into the viewport, e.g. scrolling, so then this loop is used to give such chances
            for i in range(7):
                # viewport attr
                viewport_height = self.__driver.execute_script("return window.innerHeight;")
                viewport_top = self.__driver.execute_script("return window.pageYOffset;")
                viewport_bottom = viewport_top + viewport_height

                # target element attr
                element_rect = target_element.rect
                element_top = element_rect["y"]
                element_bottom = element_top + element_rect["height"]

                if (viewport_top < element_top) and (viewport_bottom > element_bottom):
                    # The element is within the viewport
                    return True
                time.sleep(0.7)
        return False
