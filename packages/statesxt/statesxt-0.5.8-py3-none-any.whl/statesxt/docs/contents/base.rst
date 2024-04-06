#####
/base
#####

This is where all functions related to Selenium capabilities are placed.

.. figure:: /_static/images/uml-base.png
   :alt: The UML Class Diagram for ``/base``
   :width: 630
   :align: center

   **Figure 2**: The UML Class Diagram for ``/base``

Before understanding the use of each folder and the files within, It is better to know their roles in general, as Figure 2 shows the relationship between each class.

Below are some important points to understand from the Figure 2,

* Placement of each class

    * ``BaseDriver``, is placed under ``base_driver.py``,
    * ``CheckDriver``, is placed under ``check.py``,
    * ``FormDriver``, is placed under ``form.py``,
    * ``MouseKeysDriver``, is placed under ``mouse_keys.py``,
    * ``TableDriver``, is placed under ``table.py``,
    * ``WaitDriver``, is placed under ``wait.py``,
    * ``MyBy``, is placed under ``wait.py``,
* ``BaseDriver`` and ``MyBy`` would be the interfaces that connect with other files outside ``/base``,
* Most of the relations are not inheritance, instead are composition.


__init__.py
===========
Is the double underscore (dunder) init file that is used to recognize the directory, in this case is ``/base``, as a Python package. This file does not contain anything.


base_driver.py
==============
Acts as the interface that connects every functions inside ``/base`` folder to outside. So, most of the other files, e.g. ``check.py``, ``form.py``, are initialized inside, as the attributes of ``BaseDriver`` as shown below.

.. code-block:: python

    class BaseDriver:
    """Wraps driver and provides all common-used WebDriver actions"""

    def __init__(self, browser, fullscreen=True, duration: int = 27) -> None:
        self.setup(browser, fullscreen)

        self.cd = CheckDriver(self.__driver, duration)
        self.fd = FormDriver(self.__driver, duration)
        self.mkd = MouseKeysDriver(self.__driver)
        self.td = TableDriver(self.__driver, duration)
        self.wd = WaitDriver(self.__driver, duration)

Additionally, ``BaseDriver`` also holds some methods,

.. code-block:: python

    def setup(self, browser, fullscreen) -> None:
        """Sets up which browser to use"""

        try:
            # setup driver
            start = time.time()
            if browser == "brave":
                self.__driver = webdriver.Chrome(
                    service=BraveService(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install())
                )
            elif browser == "chrome":
                self.__driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
            elif browser == "edge":
                self.__driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
            elif browser == "firefox":
                self.__driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
            end = time.time()
            print(f"\n\nsetting up driver takes {end-start} seconds to complete")

            # setup screen size
            if fullscreen:
                self.__driver.maximize_window()
        except Exception as e:
            logging.getLogger(f"root.{__name__}.{self.__class__.__name__}.{sys._getframe().f_code.co_name}").error(
                f"in the process of running setup:\n{str(e)}"
            )
            raise Exception(str(e))


The above code, is the method that is used as the configuration process of Selenium, e.g. to set which browser to be used and whether it would be executed in fullscreen or not. 

.. code-block:: python

    def navigate(self, url: str) -> None:
        """Loads a web page in the current browser session"""

        self.__driver.get(url)
        self.focus_to()

    def focus_to(self, index: int = -1) -> None:
        """Changes the focus of the driver"""

        self.__driver.switch_to.window(self.__driver.window_handles[index])

    def close_tab(self) -> None:
        """Closes the current tab, and backs to the initial tab"""

        self.__driver.close()
        self.focus_to(0)

    def exit(self) -> None:
        self.__driver.quit()

    def go_to(self, href: str):
        self.__driver.get(href)

While for some other methods, like above, are used to interact with browser in general, meaning that the capabilities are not bound only to a certain website, e.g. which tab of browser should be put the focus on or even to close the browser.


check.py
========
This file holds methods that are used to do some additional checking that are found to be so repetitive if they are placed directly on test scenarios.

.. code-block:: python

    class CheckDriver:
        def __init__(self, driver: WebDriver, duration: int) -> None:
            self.wd = WaitDriver(driver, duration)
            self.mkd = MouseKeysDriver(driver)
            self.__driver = driver

From above, those are the attributes. First, it uses ``WaitDriver`` to handle website elements. Next, it also uses ``MouseKeysDriver`` to get the capabilities of mouse and keyboard. Lastly, it assigns a driver, that keeps the whole methods of this class to work on the same browser.    

Following are the explanations of each method,

``check_viewport``
------------------

.. code-block:: python

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

Can be used to check if an element is within the current viewport. This method is very useful when you often get ``MoveTargetOutOfBoundsException`` error. Basically, it happens because you want to interact with an element that is not within the browser's visible viewport. But, still, that does not mean if all elements should be within before you make some actions. You can achive this by inspecting the elements. 

``check_alert``
---------------

.. code-block:: python

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
            eAlert = self.wd.an_element(By.CLASS_NAME, "toast-body")
            if isSuccess:
                if eAlert.text == "success" or eAlert.text == cust_message:
                    return True
            else:
                if eAlert.text == "fail" or eAlert.text == cust_message:
                    return True
            return False
        else:
            eAlert = self.wd.invisible(By.CLASS_NAME, "toast-body")
            return True if eAlert else False

It is very often right to see a similar alert component that could appear almost like in every page? The difference is always only in the message, or the color. That is why, the above code was made. Also, it is very likely that the method requires you to change it, you need to understand it at least to rename the message, or even maybe to add another configuration, e.g. about color variations.

``check_indicator_row``
-----------------------

.. code-block:: python

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

This method is used to check the presence of a row inside table that has scrolling bar since the amount of data is quite large. 

The confusing part of this method is very likely the parameter. You need to assign two values,

* ``available_rows`` should contain a list of WebElement objects. For futher information about the object, you can check it out `here <https://www.selenium.dev/documentation/webdriver/elements/>`_,
* ``target_row`` should contain a list of data that you want to find. The number of it would determine the looping range inside the sub-function, ``get_data_of_a_row``. But also, it assumes that the data is ordered next to each other.


form.py
=======
This file contains all functions related to filling a form. 

Following are the attributes of the class ``FormDriver``.

.. code-block:: python

    class FormDriver:
        def __init__(self, driver: WebDriver, duration: int) -> None:
            self.ac = ActionChains(driver)
            self.mkd = MouseKeysDriver(driver)
            self.wd = WaitDriver(driver, duration)

First, it has ``ActionChains`` that allows to chain together a series of actions and then perform them as a single action. It is very usefull, because the actions are treated as a single "atomic" action, which means that if any action in the chain fails, the entire chain is considered to have failed, and no partial interactions are performed.

Next, it also uses ``MouseKeysDriver`` to have control of mouse and keyboard. Lastly, it uses ``WaitDriver`` to get website elements.

Following are the explanations of each method,

``insert_to_textbox``
---------------------

.. code-block:: python

    def insert_to_textbox(
        self,
        element: Union[WebElement, Callable[[], WebElement]],
        input: str,
        byEnter: bool = False,
        sleep: float = 0.45,
        onFocus: bool = False,
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

        if input or (input == ""):
            if isinstance(element, Callable):
                element = element()
            if onFocus:
                self.mkd.scrolling(element)
            self.ac.pause(sleep).click(element).send_keys(Keys.END).key_down(Keys.SHIFT).send_keys(Keys.HOME).key_up(
                Keys.SHIFT
            ).send_keys(Keys.BACKSPACE).send_keys(input).perform()

            if byEnter:
                self.ac.pause(sleep).send_keys(Keys.ENTER).perform()

            self.ac.reset_actions()

As the name, this method is used to insert text to a textbox element. It has several parameters that you can use in order to reduce unexpected errors from occurring. This approach is commonly referred to as as flaky test.

``select_period``
-----------------

.. code-block:: python

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
            if onFocus:
                self.mkd.scrolling(date_input_element)

            start_date: list[int]
            end_date: list[int]
            start_date, end_date = Formatter().convert_period(period)

            # click the period date element
            date_input_element.click()

            # provide prev and next month button
            click_prev = lambda: self.wd.wdw.until(
                lambda d: date_input_element.find_element(By.XPATH, prev_button_locator)
            ).click()
            click_next = lambda: self.wd.wdw.until(
                lambda d: date_input_element.find_element(By.XPATH, next_button_locator)
            ).click()

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
            date_header = self.wd.wdw.until(
                lambda d: date_input_element.find_element(By.XPATH, date_header_locator)
            ).text.split()
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

``select_opt_in_dropdown``
--------------------------

.. code-block:: python

    def select_opt_in_dropdown(
        self,
        element: Union[WebElement, Callable[[], WebElement]],
        option,
        method="visible_text",
        onFocus: bool = False,
    ):
        if option:
            if isinstance(element, Callable):
                element = element()
            if onFocus:
                self.mkd.scrolling(element)
            select = Select(element)

            if method == "value":
                select.select_by_value(option)
            elif method == "visible_text":
                select.select_by_visible_text(option)

Is designed for interacting with dropdown elements on a webpage. It takes parameters including the dropdown element, the desired option, and an optional method parameter specifying the selection method (either by ``value`` or ``visible_text``). 

Additionally, there's an optional ``onFocus`` parameter that, when set to ``True``, triggers scrolling to bring the dropdown into focus before interacting with it. The method uses the ``Select`` class from Selenium to perform the selection based on the specified method and option.

``select_opt_in_radio``
-----------------------

.. code-block:: python

    def select_opt_in_radio(self, elements: Union[list[WebElement], Callable[[], list[WebElement]]], option: str):
        if isinstance(elements, Callable):
            elements = elements()
        clickables, menus = [[c for c in elements[::2]], [str(m.text).lower() for m in elements[1::2]]]
        index = menus.index(option.lower())
        if index:
            clickables[index].click()

This method is used for interacting with a set of radio buttons or clickable elements on a webpage. It is designed to handle scenarios where the radio buttons are associated with specific labels or options.

``check_a_box``
---------------

.. code-block:: python

    def check_a_box(self, element: WebElement, isChecked: bool):
        if element.is_selected():
            None if isChecked else element.click()
        else:
            element.click() if isChecked else None

The method is designed to interact with a checkbox element on a webpage.

mouse_keys.py
=============

.. code-block:: python

    class MouseKeysDriver:
    """
    Provides Mouse and Keys capabilities. 
    """

    def __init__(self, driver: WebDriver) -> None:
        self.ac = ActionChains(driver)
        self.__driver = driver

The ``MouseKeysDriver`` class provides capabilities for interacting with a web page using mouse and keyboard actions. It is designed to work with a Selenium WebDriver. In its ``__init__`` method, it initializes an ActionChains instance (``self.ac``) from Selenium's ActionChains module, and it stores a reference to the WebDriver as ``self.__driver``. The ActionChains instance allows the class to chain together mouse and keyboard actions, enabling more complex interactions with the web page. This class can be used as a component to perform various mouse and keyboard operations during automated testing or web scraping.

Following are the explanations of each method,

``hovering``
------------

.. code-block:: python

    def hovering(
        self,
        element: Union[WebElement, Callable[[], WebElement]],
        isHover: bool = True,
        onFocus: bool = False,
    ) -> None:
        if isHover:
            if isinstance(element, Callable):
                element = element()
            if onFocus:
                self.scrolling(element)
            self.ac.move_to_element(element).perform()
            self.ac.reset_actions()

This method handles hover actions on a web page. It takes an element, either a WebElement or a Callable returning one. If ``isHover`` is ``True``, it performs a hover action on the element. If the element is callable, it's invoked, and if ``onFocus`` is ``True``, a scrolling action is executed before hovering. The function utilizes Selenium's ActionChains for mouse movement and resets actions afterward.

``scrolling``
-------------

.. code-block:: python

    def scrolling(
        self,
        element: Union[WebElement, Callable[[], WebElement]] = None,
        isScroll: bool = True,
        steps: int = None,
        block: str = "center",
        sleep: float = 0.75,
    ) -> None:
        """
        'block', defines vertical alignment.
        - 'start',
        - 'center' (default),
        - 'end',
        - 'nearest'.
        """

        if isScroll:
            if element:
                if isinstance(element, Callable):
                    element = element()
                if steps:
                    print(f"steps: {steps}")
                    self.ac.scroll_by_amount(0, steps).pause(sleep).perform()
                    self.__driver.execute_script("arguments[0].scrollIntoView();", element)
                else:
                    self.__driver.execute_script("arguments[0].scrollIntoView({block: '" + block + "'});", element)
                    time.sleep(sleep)
            else:
                self.ac.scroll_by_amount(0, steps).pause(sleep).perform()
                self.ac.reset_actions()

The method handles scrolling on a web page. It takes parameters such as the target element, a flag to determine if scrolling is needed, the number of steps, vertical alignment, and sleep duration. The function is essential for ensuring the visibility of elements on a webpage, providing flexibility in scrolling options.

``clicking``
------------

.. code-block:: python

    def clicking(
        self,
        element: Union[WebElement, Callable[[], WebElement]],
        isClick: bool = True,
        sleep: float = 0.36,
        steps: int = None,
        block: str = "center",
    ) -> None:
        if isClick:
            if isinstance(element, Callable):
                element = element()
            if sleep >= 0.36:
                self.scrolling(element=element, steps=steps, block=block, sleep=sleep)
            element.click()

This manages click actions on a web page. It accepts parameters such as the target element (element), a boolean flag (``isClick``) for deciding whether to click, a sleep duration (``sleep``) to ensure element visibility, and scrolling parameters (steps and block). The function is crucial for automating user interactions, ensuring proper visibility and interaction with elements on the webpage.

``pressing_keys``
-----------------

.. code-block:: python

    def pressing_keys(self, options: str) -> None:
        keys = {
            "esc": Keys.ESCAPE,
            "enter": Keys.ENTER,
        }
        self.ac.send_keys(keys[options]).perform()
        self.ac.reset_actions()

This method handles key pressing actions on a web page. It takes a string parameter (options) specifying the key to press, such as "esc" for the ``Escape`` key or "enter" for the Enter key. The function utilizes a dictionary (keys) to map options to corresponding Selenium Keys. The ActionChains (``self.ac``) are then used to send the key press and actions are reset afterward. This function is essential for simulating keyboard interactions during automated testing or web scraping.

``zooming``
-----------

.. code-block:: python

    def zooming(self, zoom_percentage: float, sleep: int = 1) -> None:
        """
        Zooms in and out the screen.

        Args:
            - zoom_percentage (float), is the percentage of the screen wanted to be
        """
        self.__driver.execute_script(f"document.body.style.zoom = '{zoom_percentage/100}';")
        time.sleep(sleep)

This method dynamically adjusts the screen's zoom level, offering a programmatic means to enlarge or shrink displayed content. Users specify the desired zoom percentage as a floating-point value, and the method seamlessly applies the change using JavaScript execution within the browser environment. This functionality proves essential for tasks requiring magnified detail inspection or overall content scaling, enhancing both visual accessibility and user experience.

``paginating``
--------------

.. code-block:: python

    def paginating(
        self,
        target_row: list[str],
        func_get_paginations: Callable[[], list[WebElement]],
        func_check_rows: Callable[[list[str]], bool],
        direction: str = "backward",
        tobeFound: bool = True,
        sleep: float = 0,
    ):
        def get_list_of_pagination_numbers():
            raw_pns = func_get_paginations()
            pns = []
            titles = []
            for pn in raw_pns:
                title = pn.get_attribute("title")
                if title in [
                    "previous page",
                    "next page",
                    "first page",
                    "last page",
                ]:
                    pns.append(pn)
                    titles.append(title)
            return [pns, titles]

        def click_page_number(title: str, pns: list[WebElement], titles: list[str]):
            """
            - clicks the title page and updates the pagination numbers, and their titles
            - title is whether 'previous page','next page','first page', or 'last page'
            """

            pn = pns[titles.index(title)]
            self.scrolling(element=pn)
            pn.click()
            return get_list_of_pagination_numbers()

        pns, titles = get_list_of_pagination_numbers()
        if direction == "backward":
            # go to the last page
            if "last page" in titles:
                pns, titles = click_page_number(title="last page", pns=pns, titles=titles)
            else:
                # backwarding (without checking)
                while "next page" in titles:
                    pns, titles = click_page_number(title="next page", pns=pns, titles=titles)

        # checking while also backwarding
        occur = 0
        while occur < 1:
            # check whether or not the condition is ready to stop
            if (
                ("previous page" not in titles) if (direction == "backward") else ("next page" not in titles)
            ):  # when in page item-1
                occur += 1
            # check current page's rows
            time.sleep(sleep)
            if func_check_rows(target_row):
                return True if tobeFound else False
            # forwarding / backwarding (depends on the direction)
            if occur != 1:
                pns, titles = (
                    click_page_number(title="previous page", pns=pns, titles=titles)
                    if (direction == "backward")
                    else click_page_number(title="next page", pns=pns, titles=titles)
                )
        return False if tobeFound else True

This method automates page navigation through multi-page data, seeking a specific row. You define what the row looks like (``target_row``) and how to find pagination buttons (``func_get_paginations``). It then intelligently clicks through pages (forward or backward) until it finds the row or reaches the end, depending on your goal. This powerful method saves time and effort when searching large datasets with paginated displays.


table.py
========

This file contains every functions related to work with data in a table.

.. code-block:: python

    class TableDriver:
    """
    Provides the capability to interact with tables.
    """

    def __init__(self, driver, duration: int) -> None:
        self.ft = Formatter()
        self.ac = ActionChains(driver)
        self.wd = WaitDriver(driver, duration)

It uses Formatter, from ``/utils/formatter.py``, to format some data. Then, it also uses ActionChains and WaitDriver.

Following are the explanations of each method,

``get_table_rows``
------------------

.. code-block:: python

    def get_table_rows(self, table: WebElement):
        tbody = table.find_element(By.TAG_NAME, "tbody")
        return tbody.find_elements(By.TAG_NAME, "tr")

``get_table_cols``
------------------

.. code-block:: python

    def get_table_cols(self, row: WebElement):
        return row.find_elements(By.TAG_NAME, "td")

``get_data_on_hint``
--------------------

.. code-block:: python

    def get_data_on_hint(self, hoverable_element, hint_table, hint_header, ignored_columns):
        self.ac.move_to_element(hoverable_element).perform()
        rows = self.wd.all_elements(By.XPATH, hint_table)
        result = []
        for row in rows if hint_header else rows[1:]:
            cols = row.find_elements(By.TAG_NAME, "div")
            result.append([self.ft.convert_number(cols[i].text) for i in range(len(cols)) if i not in ignored_columns])
        return result

``get_attribute``
-----------------

.. code-block:: python

    def get_attribute(self, element, option=[]):
        if "color" in option:
            if element.text == "":
                return None
            return self.ft.rgba_string_to_hex(element.value_of_css_property("color"))

``get_data_from_table``
-----------------------

.. code-block:: python

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
                        temp[column_names[j]] = [
                            self.ft.convert_number(s.replace("%", "").strip("'"))
                            for s in repr(cols[j].text).split("\\n")
                        ] + [self.get_data_on_hint(cols[j], hint_table, hint_header, ignored_hint_columns)]
                        continue
                    if j in attribute:
                        temp[column_names[j]] = [
                            self.ft.convert_number(s.replace("%", "").strip("'")) if (s != "''") else None
                            for s in repr(cols[j].text).split("\\n")
                        ] + [self.get_attribute(cols[j], option=["color"])]
                        continue
                    temp[column_names[j]] = [
                        self.ft.convert_number(s.replace("%", "").strip("'")) if (s != "''") else None
                        for s in repr(cols[j].text).split("\\n")
                    ]
                data.append(temp)

        return data

wait.py
=======

.. code-block:: python

    class MyBy:
        """
        Provides keys that each links to an 'By' object.
        The purpose is to have control to By objects name.
        
        For example: 
        If we want to rename one of the keys, that can be done by renaming it just in here.
        Of course do not forget to use F2 before renaming it, so it applies to all references.
        """

        xpath = By.XPATH
        css = By.CSS_SELECTOR
        cname = By.CLASS_NAME
        id = By.ID
        link = By.LINK_TEXT
        plink = By.PARTIAL_LINK_TEXT
        name = By.NAME
        tag = By.TAG_NAME

.. code-block:: python

    class WaitDriver:
        """
        Provides explicit wait, i.e. will wait until either the element has found or exceed time limit.
        """

        def __init__(self, driver, duration: int) -> None:
            self.init_duration = duration
            self.wdw = WebDriverWait(driver, duration)


Following are the explanations of each method,

``an_element``
--------------

.. code-block:: python
    
    @Wrapper.exception_handling_returns_None
    def an_element(self, by: MyBy, locator, custom_duration: float = 0) -> WebElement:
        if custom_duration > 0:
            self.wdw._timeout = custom_duration
        res = self.wdw.until(EC.presence_of_element_located((by, locator)))
        self.wdw._timeout = self.init_duration
        return res

``all_elements``
----------------

.. code-block:: python

    @Wrapper.exception_handling_returns_None
    def all_elements(self, by: MyBy, locator, custom_duration: float = 0) -> list[WebElement]:
        if custom_duration > 0:
            self.wdw._timeout = custom_duration
        res = self.wdw.until(EC.presence_of_all_elements_located((by, locator)))
        self.wdw._timeout = self.init_duration
        return res

``clickable``
-------------

.. code-block:: python

    @Wrapper.exception_handling_returns_None
    def clickable(self, by: MyBy, locator, custom_duration: float = 0) -> WebElement:
        if custom_duration > 0:
            self.wdw._timeout = custom_duration
        res = self.wdw.until(EC.element_to_be_clickable((by, locator)))
        self.wdw._timeout = self.init_duration
        return res

``visible``
-----------

.. code-block:: python

    @Wrapper.exception_handling_returns_None
    def visible(self, by: MyBy, locator, custom_duration: float = 0) -> WebElement:
        if custom_duration > 0:
            self.wdw._timeout = custom_duration
        res = self.wdw.until(EC.visibility_of_element_located((by, locator)))
        self.wdw._timeout = self.init_duration
        return res

``invisible``
-------------

.. code-block:: python

    @Wrapper.exception_handling_returns_None
    def invisible(self, by: MyBy, locator, custom_duration: float = 0) -> bool:
        if custom_duration > 0:
            self.wdw._timeout = custom_duration
        res = self.wdw.until(EC.invisibility_of_element_located((by, locator)))
        self.wdw._timeout = self.init_duration
        return res