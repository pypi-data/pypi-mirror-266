from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from utils.formatter import Formatter
from .wait import WaitDriver


class TableDriver:
    """
    Provides the capability to interact with tables.
    """

    def __init__(self, driver, duration: int) -> None:
        self.ft = Formatter()
        self.ac = ActionChains(driver)
        self.wd = WaitDriver(driver, duration)

    def get_attribute(self, element, option=[]):
        if "color" in option:
            if element.text == "":
                return None
            return self.ft.rgba_string_to_hex(element.value_of_css_property("color"))

    def get_data_from_table(
        self,
        table: WebElement,
        hint_table=None,
        hint_header=False,
        column_names=[],
        attribute=[],
        ignored_table_columns_to_hover=[],
        ignored_table_rows_to_hover=[],
        ignored_hint_columns=[],
    ):
        rows = self.get_table_rows(table)
        data = []
        for i in range(len(rows)):
            cols = self.get_table_cols(rows[i])
            temp = {}
            if i not in ignored_table_rows_to_hover:
                for j in range(len(cols)):
                    if (hint_table) and (j not in ignored_table_columns_to_hover):
                        temp[column_names[j]] = [self.ft.convert_number(s.replace("%", "").strip("'")) for s in repr(cols[j].text).split("\\n")] + [
                            self.get_data_on_hint(cols[j], hint_table, hint_header, ignored_hint_columns)
                        ]
                        continue
                    if j in attribute:
                        temp[column_names[j]] = [self.ft.convert_number(s.replace("%", "").strip("'")) if (s != "''") else None for s in repr(cols[j].text).split("\\n")] + [
                            self.get_attribute(cols[j], option=["color"])
                        ]
                        continue
                    temp[column_names[j]] = [self.ft.convert_number(s.replace("%", "").strip("'")) if (s != "''") else None for s in repr(cols[j].text).split("\\n")]
                data.append(temp)

        return data

    def get_data_on_hint(self, hoverable_element, hint_table, hint_header, ignored_columns):
        self.ac.move_to_element(hoverable_element).perform()
        rows = self.wd.all_elements(By.XPATH, hint_table)
        result = []
        for row in rows if hint_header else rows[1:]:
            cols = row.find_elements(By.TAG_NAME, "div")
            result.append([self.ft.convert_number(cols[i].text) for i in range(len(cols)) if i not in ignored_columns])
        return result

    def get_table_cols(self, row: WebElement):
        return row.find_elements(By.TAG_NAME, "td")

    def get_table_rows(self, table: WebElement):
        tbody = table.find_element(By.TAG_NAME, "tbody")
        return tbody.find_elements(By.TAG_NAME, "tr")
