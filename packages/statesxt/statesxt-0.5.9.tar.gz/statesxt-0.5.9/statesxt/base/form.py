from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.edge.webdriver import WebDriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime
from typing import Callable
from typing import Union

from .mouse_keys import MouseKeysDriver
from utils.formatter import Formatter
from .wait import WaitDriver


class FormDriver:
    def __init__(self, driver: WebDriver, duration: int) -> None:
        self.ac = ActionChains(driver)
        self.mkd = MouseKeysDriver(driver)
        self.wd = WaitDriver(driver, duration)

    def check_a_box(
        self,
        element: WebElement,
        isChecked: bool,
        onFocus: bool = False,
        sleep: float = None,
    ):
        if onFocus or sleep:
            self.mkd.scrolling(element, sleep)
        if element.is_selected():
            None if isChecked else element.click()
        else:
            element.click() if isChecked else None

    def get_selected_option(
        self,
        element: WebElement,
    ):
        return Select(element).first_selected_option

    def insert_to_textbox(
        self,
        element: Union[WebElement, Callable[[], WebElement]],
        input: str,
        byEnter: bool = False,
        onFocus: bool = True,
        sleep: float = None,
        isInserted: bool = True,
    ) -> None:
        """
        Inserts string into a textbox element

        Args:
            element (WebElement): is the input element
            input (str): is the string to be inputted
            byEnter (bool): is the final action, e.g. True means the enter key will be pressed
            sleep: duration between action
            onFocus: to scroll before inserting

        Returns:
            None
        """

        if isInserted:
            if input or (input == ""):
                if isinstance(element, Callable):
                    element = element()
                if onFocus or sleep:
                    self.mkd.scrolling(element, sleep)

                self.ac.click(element).send_keys(Keys.END).key_down(Keys.SHIFT).send_keys(Keys.HOME).key_up(Keys.SHIFT).send_keys(Keys.BACKSPACE).send_keys(input).perform()

                if byEnter:
                    self.ac.send_keys(Keys.ENTER).perform()

                self.ac.reset_actions()

                # for faster approach
                # textbox_element.click()
                # textbox_element.clear()
                # textbox_element.send_keys(input)
                # textbox_element.send_keys(Keys.ENTER)

    def select_opt_in_dropdown(
        self,
        element: Union[WebElement, Callable[[], WebElement]],
        option,
        method="visible_text",
        onFocus: bool = False,
        sleep: float = None,
    ):
        if option:
            if isinstance(element, Callable):
                element = element()
            if onFocus or sleep:
                self.mkd.scrolling(element, sleep)

            select = Select(element)
            if method == "value":
                select.select_by_value(option)
            elif method == "visible_text":
                select.select_by_visible_text(option)

    def select_opt_in_radio(
        self,
        elements: Union[list[WebElement], Callable[[], list[WebElement]]],
        option: str,
        onFocus: bool = False,
        sleep: float = None,
    ):
        if isinstance(elements, Callable):
            elements = elements()
        clickables, menus = [
            [c for c in elements[::2]],
            [str(m.text).lower() for m in elements[1::2]],
        ]
        index = menus.index(option.lower())
        if onFocus or sleep:
            self.mkd.scrolling(clickables[index], sleep)
        clickables[index].click()

    def select_period(
        self,
        period: str,
        date_input_element: WebElement,
        prev_button_locator,
        next_button_locator,
        date_header_locator,
        date_per_week_locator,
        date_per_day_locator,
        onFocus: bool = False,
        sleep: float = None,
    ):
        """
        Input value into the period element

        Args:
            period (str): is the date/period
            input (str): is the string to be inputted
            byEnter (bool): is the final action, e.g. True means the enter key will be pressed

        Returns:
            None
        """

        if period:
            if onFocus or sleep:
                self.mkd.scrolling(date_input_element, sleep)

            start_date: list[int]
            end_date: list[int]
            start_date, end_date = Formatter().convert_period(period)

            # click the period date element
            date_input_element.click()

            # provide prev and next month button
            click_prev = lambda: self.wd.wdw.until(lambda d: date_input_element.find_element(By.XPATH, prev_button_locator)).click()
            click_next = lambda: self.wd.wdw.until(lambda d: date_input_element.find_element(By.XPATH, next_button_locator)).click()

            def prev_and_next(num_of_clicks: int):
                if num_of_clicks > 0:
                    for _ in range(num_of_clicks):
                        click_next()
                else:
                    for _ in range(abs(num_of_clicks)):
                        click_prev()

            def select_date(selected_date: str):
                week_elements = self.wd.all_elements(By.CLASS_NAME, date_per_week_locator)
                day_elements = self.wd.all_elements(By.CLASS_NAME, date_per_day_locator)
                day_elements_per_week = []
                for i in range(len(week_elements)):
                    el = day_elements[(i * 7) : ((i + 1) * 7)]
                    day_elements_per_week.append(el)

                isFound = False
                num_of_weeks = len(day_elements_per_week)
                for i in range(num_of_weeks):
                    for date in day_elements_per_week[i]:
                        if (i == 0 and int(date.text) > 7) or (i == num_of_weeks and int(date.text) < 20):
                            continue
                        if date.text == selected_date:
                            date.click()
                            isFound = True
                            break
                    if isFound:
                        break

            # get current date
            date_header = self.wd.wdw.until(lambda d: date_input_element.find_element(By.XPATH, date_header_locator)).text.split()
            cur_month = int(datetime.strptime(date_header[0], "%B").month)
            cur_year = int(date_header[1])

            # get number of clicks needed to reach the start_date
            month_diff_with_curr = start_date[1] - cur_month
            year_diff_with_curr = start_date[0] - cur_year
            start_clicks = 0
            start_clicks += month_diff_with_curr
            start_clicks += year_diff_with_curr * 12

            # move to the month and year of the start_date
            prev_and_next(start_clicks)

            # select date of the start_date
            select_date(selected_date=str(start_date[2]))

            if len(end_date) == 3:
                # get number of clicks needed to reach the end_date
                month_diff_with_end_date = end_date[1] - start_date[1]
                year_diff_with_end_date = end_date[0] - start_date[0]
                end_clicks = 0
                end_clicks += month_diff_with_end_date
                end_clicks += year_diff_with_end_date * 12

                # move to the month and year of the end_date
                prev_and_next(end_clicks)

                # select date of the end_date
                select_date(selected_date=str(end_date[2]))

            date_input_element.click()
