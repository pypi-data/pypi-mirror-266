##########
/testcases
##########

This folder mostly contain test scenarios categorized by page. While the rest are fixtures, interfaces, and states.

.. note::
    There are few files/folders that the naming begins with ``_``. The reason is simply so that they will be placed at the beginning of the folder they are in, which in this case is ``/testcases``.


/_fixtures
==========
This folder contains fixtures.

A fixture is a Pytest feature that provides a way to set up and tear down resources or perform setup and cleanup operations before and after tests. In Python, setup are all the codes before ``yield``, while teardown are all after it.

A fixture function in Pytest is marked with the ``@pytest.fixture`` decorator. When a test function includes the fixture function as an argument, Pytest automatically invokes the fixture function and passes its return value to the test function. This allows you to perform setup operations, provide data, or create resources that are required for the test.


__init__.py
-----------
This dunder init file does not contain anything, so its presence only to recognize the directory, which in this case is ``/_fixtures``, as a Python package.


composition_fixture.py
----------------------
This file contains all composition fixtures. They are called as a composition because the way they are most likely to be used is as a composition, i.e. defining an instance into a class attribute.

These are several composition fixtures you can use,

* ``logger``

  .. code-block:: python

    @pytest.fixture(scope="session")
    def logger():
        lg = Logger()
        yield
        lg.shutdown()

  This fixture's scope is session, meaning that it will be destroyed at the end of the test session.

  Inside the function's setup, it defines a Logger from ``/utils/logger.py``. Meanwhile, in the teardown, it shutdowns the Logger instance.
    
* ``gsheet``

  .. code-block:: python

    @pytest.fixture(scope="session")
    @pytest.mark.usefixtures("use_gsheet")
    @pytest.mark.usefixtures("tfo")
    def gsheet(request, use_gsheet, tfo):
        usedMarkers = request.config.getoption("-m").split(" and ")
        if "scheduler" in usedMarkers:
            yield None
            return
        gsheet_statesxt = GSheetStateSXT(
            spreadsheetName=os.getenv("SPREADSHEET_NAME"),
            folderId=os.getenv("FOLDER_ID"),
            testedFilesOnly=False if (tfo == "0") else True,
        )
        yield gsheet_statesxt
        if use_gsheet == "1":
            print("updating gsheet...")
            gsheet_statesxt.update_all_values()
            gsheet_statesxt.update_worksheet_colors()

  This fixture has several decorators. The ``@pytest.fixture(scope="session")`` is used to declare this function as a fixture with ``session`` as the scope, meaning that it will be destroyed at the end of the test session. As for the rest, are implementing other fixtures into this function that each to give the capability to insert a configuration into CLI, e.g. ``@pytest.mark.usefixtures("use_gsheet")`` enables you to use parameter ``use_gsheet``, which the value either 0 or 1, into CLI.

  Inside the function's setup, it enables an option ``-m`` into CLI and defines a GSheet instance. Meanwhile, in the teardown, it invokes some methods from the GSheet instance if the value of ``use_gsheet`` is 1.
    

* ``email``

  .. code-block:: python

    @pytest.fixture(scope="session")
    @pytest.mark.usefixtures("use_email")
    def email(use_email):
        # create an email instance
        email = EmailScheduler(
            sender_email=os.getenv("SENDER_EMAIL"),
            sender_password=os.getenv("SENDER_PASSWORD"),
            receiver_email=os.getenv("RECEIVER_EMAIL").split(","),
            receiver_name=os.getenv("RECEIVER_NAME").split(","),
        )
        yield email
        print(f"\n\nResults:\n{email.testResult}\n")
        if use_email == "1":
            # send email
            try:
                print("Sending email...")
                email.send()
                print("Email has been sent successfully.")
            except Exception as e:
                print(f"Email failed to send: {str(e)}")

  This fixture has 2 decorators. The ``@pytest.fixture(scope="session")`` is used to declare this function as a fixture with ``session`` as the scope, meaning that it will be destroyed at the end of the test session. Meanwhile, ``@pytest.mark.usefixtures("use_email")`` is implementing another fixture into this function that gives the capability to insert a configuration into CLI.

  Inside the function's setup, it defines an EmailScheduler instance from ``/utils/email.py``. Meanwhile, in the teardown, it invokes some methods from the EmailScheduler instance if the value of ``use_email`` is 1.


option_fixture.py
-----------------
This file contains all option fixtures. They are called as an option because they can give the capability to insert a value for a parameter into CLI.

These are several option fixtures you can use,

* ``pytest_addoption``

  .. code-block:: python

    def pytest_addoption(parser):
        parser.addoption("--browser", "-B")
        parser.addoption("--use_gsheet")
        parser.addoption("--use_email")
        parser.addoption("--tfo")
        parser.addoption(
            "--number-help",
            action="store_true",
            default=False,
            help="Print custom number help information and exit.",
        )

  This function is a hook in the pytest framework. When pytest runs, it calls this function, passing an argument called ``parser``. which is an instance of the ``ArgumentParser`` class from the ``argparse`` module, and it is used to define command-line options for your pytest scripts. It allows to specify various options when running the pytest scripts, such as the browser to use, whether to use Google Sheets or email functionalities, and potentially some custom behavior related to numbers.

* ``browser``

  .. code-block:: python

    @pytest.fixture(scope="session")
    def browser(request):
        req = request.config.getoption("--browser") or request.config.getoption("-B")
        return req if req else "chrome"

  This fixture has a decorator, ``@pytest.fixture(scope="session")``, that is used to declare this function as a fixture with ``session`` as the scope, meaning that it will be destroyed at the end of the test session.

  This fixture allows you to specify a browser to be used in your tests through command-line options while providing a default value of "chrome" if no option is specified.


* ``use_gsheet``

  .. code-block:: python

    @pytest.fixture(scope="session")
    def use_gsheet(request):
        req = request.config.getoption("--use_gsheet")
        return req if req else "1"

  This fixture has a decorator, ``@pytest.fixture(scope="session")``, that is used to declare this function as a fixture with ``session`` as the scope, meaning that it will be destroyed at the end of the test session.

  This fixture allows you to specify whether to use Google Sheets for reporting in your tests through the ``--use_gsheet`` command-line option. If the option is not specified, the default value is "1", meaning that GSheet is used for reporting. 

* ``use_email``

  .. code-block:: python

    @pytest.fixture(scope="session")
    def use_email(request):
        req = request.config.getoption("--use_email")
        return req if req else "1"

  This fixture has a decorator, ``@pytest.fixture(scope="session")``, that is used to declare this function as a fixture with ``session`` as the scope, meaning that it will be destroyed at the end of the test session.

  This fixture allows you to specify whether to use email functionality, that is used to send email after execution ends, in your tests through the ``--use_email`` command-line option. If the option is not specified, the default value is "1", meaning that the program will send email after execution ends.

* ``tfo``

  .. code-block:: python

    @pytest.fixture(scope="session")
    def tfo(request):
        req = request.config.getoption("--tfo")
        return req if req else "1"
  
  This fixture has a decorator, ``@pytest.fixture(scope="session")``, that is used to declare this function as a fixture with ``session`` as the scope, meaning that it will be destroyed at the end of the test session.

  The name 'tfo' stands for 'tested files only'. This fixture allows you to control whether to generate a worksheet report only for the tested files in your tests using the ``--tfo`` command-line option. If the option is not specified, the default value "1" is used, indicating that the worksheet report should include only the tested files.

* ``pytest_collection_modifyitems``

  .. code-block:: python

    def pytest_collection_modifyitems(config, items):
        if config.option.number_help:
            print(
                """
            Browser:
            - 1 = brave
            - 2 = chrome
            - 3 = edge
            - 4 = firefox

            """
            )
            items.clear()

  It is a hook in the pytest framework that allows you to modify the test items collected during the test collection phase. In this specific case, it checks if the ``--number-help`` option is provided, and if so, it prints information about browser options and clears the test items. This can be helpful for providing user guidance on browser options without running the tests.


/_interfaces
============
This folder contains interface classes that are categorized based on pages.

Interface is part of the State Design Pattern. Its presence bridges the Context class and ConcreteStates classes, using Inheritance to force the childs, which are state classes, to define the abstract methods.

.. figure:: /_static/images/structure-en.png
   :alt: The State Design Pattern Structure
   :width: 450
   :align: center

   **Figure 3**: The State Design Pattern Structure


From this point onwards, there will be explanations about the relationship between classes in states. So, to help you understand of what is being explained, here is the UML of States.

.. figure:: /_static/images/uml-framework-states.png
   :alt: The UML of States
   :width: 630
   :align: center

   **Figure 4**: The UML of States

__init__.py
-----------
Besides its function to recognize the directory, which in this case is ``/_interfaces``, as a Python package, this dunder init file also contains a class called StateInterface that is the parent class of all interface classes.

.. code-block:: python

  class StateInterface(ABC):
    """
    An abstract class for all the state interface classes
    """

    def __init__(self, base: BaseDriver) -> None:
        self.__bd = base

    @property
    def bd(self):
        return self.__bd

As for the attribute, it has a ``self__bd = base`` which is a BaseDriver that will keep the execution using the same driver instance.

It has a method, which is a property of ``self__bd = base``.


example_interface.py
--------------------
This is an example of interface class. The number of this classes is proportional to the number of pages. So, along the way, for example there could be ``login_interface.py`` and ``dashboard_interface.py`` that holds interface methods for the page.

.. code-block:: python

  if TYPE_CHECKING:
      from pages.example_page import ExamplePage


  class ExampleInterface(StateInterface, ABC):
      def __init__(self, base, contextPage: "ExamplePage") -> None:
          super().__init__(base)
          self.ep = contextPage

      def clickExample(self, *args, **kwargs):
          pass

      def changeLanguage(self, *args, **kwargs):
          pass

      def success(self, *args, **kwargs):
          pass

      def error(self, *args, **kwargs):
          pass

From the above example, it has first an import inside ``TYPE_CHECKING`` conditional. It is used to define the ``contextPage`` type, so in code editor there will be highlights to some methods.

This class inherits from ``StateInterface``, which is a parent class that holds ``self__bd = base`` to keep the execution still using the same driver instance. Another than, ``super().__init__(base)``, it has ``self.ep = contextPage`` that will be used by the child class, which is a State Class, for referencing any methods of the ExamplePage.

``clickExample``, ``changeLanguage``, ``success``, and ``error`` are example interface methods. They will always be empty, represented by ``pass``. Their presence is only to bridge the relationship between Context (Page Classes) and ConcreteStates (State Class, the child of this class).


/_states
========
This folder contains state classes that are categorized based on pages.

A state is a condition. If you are familiar with State Transition Diagram (STD), a state is represented by a circle. From that STD, you also notice that each state could have some lines, which are transitions.

In Python, a state is represented by a class, which the methods are represented the possible transitions of that state. 


/example_states.py
------------------
This is an example folder that holds your states. It's actually really up to you, whether you want to separate it as folders or files.


__init__.py
~~~~~~~~~~~
This dunder init file does not contain anything, so its presence only to recognize the directory, which in this case is ``/example_states``, as a Python package.


ls001.py
~~~~~~~~
Again, this is an example of a file that holds a state class. Why is it being separated by each state and not by class? The only answer is because the number of transitions/methods that a state could have. So, in order to make it more maintainable, it is separated deeper.

.. code-block:: python

  class ExamplePageState(ExampleInterface):
      def __init__(self, base, contextPage) -> None:
          super().__init__(base, contextPage)

      def changeLanguage(self, lang):
          # required process
          if lang in self.ep.jpnFormats:
              self.bd.mkd.clicking(self.ep.lr.JPN_FLAG_BUTTON(), sleep=0)
          elif lang in self.ep.engFormats:
              self.bd.mkd.clicking(self.ep.lr.ENG_FLAG_BUTTON(), sleep=0)
          # transition
          self.ep.changeState(ExamplePageState(self.bd, self.ep))

A state class inherits a page interface class. Inside each method, for example changeLanguage, it has at least 2 part of code, which are 'required process' and 'transition'. Required process is like prerequisite to go to the next step. Meanwhile, transition will always has the same invoked method, which is changeState, that is used to go to the next state.


__init__.py
-----------
This dunder init file does not contain anything, so its presence only to recognize the directory, which in this case is ``/_states``, as a Python package.


/example
========
This folder holds the scenarios of a page. As an example, for a login page, then this folder name is ``/login``, and that's it. Because of that, the folder ``/testcases`` will be populated mostly with this type of folder.


__init__.py
-----------
Besides its function to recognize the directory, which in this case is ``/example``, as a Python package, this dunder init file also contains a class called TestExample that is the parent class of all scenario classes.

.. code-block:: python

  @pytest.mark.order(1)
  @pytest.mark.usefixtures("setup")
  class TestExample(softest.TestCase):
      """Test cases for example page"""

      @pytest.fixture(autouse=True)
      def class_setup(self):
          self.ep = ExamplePage(self.base)

The above class has 2 decorators prefixed with @. ``@pytest.mark.order(1)`` tells Pytest to execute the child scenarios of this class first. You can absolutely change the order to suit your desire. Usually it is the best to do it by priority. Next, it also has ``@pytest.mark.usefixtures("setup")`` to use setup fixture from ``./conftest``. 


test_0_1.py
-----------
This is an example of a scenario class that holds scenarios represented by methods. Not like the other files/folders where you can rename as you want, an exeception for this type of file, you can't change the prefix ``test_`` because it is the way Pytest recognizes these files as scenarios/to be executed.

.. code-block:: python

  @pytest.mark.dev
  class TestExample01(TestExample):
      def __init__(self, methodName: str = "runTest"):
          super().__init__(methodName)

      @Wrapper.result_receiving
      @Wrapper.unpagshe(*("0.1", "_SN_0_1_Scenario_001_Data"))
      def test_scenario001(self, *args):
          """Test Scenario: 1-1"""

          # change language   (1-1)
          self.soft_assert(self.assertIsNone, self.ep.changeLanguage(lang=args[0]))

          self.assert_all()

The above class has a mark, ``@pytest.mark.dev``, that is used for execution. Basically, it will tell the program to execute the scenarios within only. But, it will only work when you add the ``-m dev`` into CLI. It can be placed on each scenario, or even the parent class of this. In case you want to rename the marker or even to add more, you can do it in ``./pytest.ini`` file.

Next, there is a ``test_scenario001`` method which represents a scenario. It has 2 decorators that are both from ``./utils/wrapper.py``. The first decorator, ``@Wrapper.result_receiving``, is used to get the name of the scenario as in the setup. Meanwhile in the teardown, it will record the result of this scenario execution to be used later for email or gsheet reporting, and to raise an error in case of something unexpected happens. The second decorator, ``@Wrapper.unpagshe(*("0.1", "_SN_0_1_Scenario_001_Data"))`` stands for unpack google sheet, is used to retrieve the data from Google Sheet. It uses name of a worksheet, e.g. ``0.1``, and a named range, e.g. ``_SN_0_1_Scenario_001_Data``.

Inside the scenario method, each state is covered with ``soft_assert`` that is used to capture the result. So most likely, there will be many ``soft_assert``. It has 2 parameters, first is the expected result, that you can find it more `here <https://docs.python.org/3/library/unittest.html#assert-methods>`_, and second is the state. 

At the end, you should always add ``self.assert_all()`` to summary the result of ``soft_assert()``


__init__.py
===========
Besides its function to recognize the directory, which in this case is ``/testcases``, as a Python package, this dunder init file also invokes a method ``load_dotenv()`` to retrieve all values from ``.env``.


conftest.py
===========
This file will be executed first by Pytest. This file allows you to define fixtures, hooks, and other configurations that can be shared across multiple test files within a directory or its subdirectories. It's a convenient way to organize and share common testing-related code. Pytest will automatically discover and use the fixtures, hooks, and other configurations defined in this file. 

.. code-block:: python

  @pytest.fixture(scope="class")
  @pytest.mark.usefixtures("logger")
  @pytest.mark.usefixtures("browser")
  @pytest.mark.usefixtures("gsheet")
  @pytest.mark.usefixtures("email")
  def setup(request, logger, browser, gsheet, email):
      logger

      # setup driver
      base = BaseDriver(browser, fullscreen=True)

      # setup service
      service = DBService()
      service.start()

      # set requests
      request.cls.base = base
      request.cls.service = service
      request.cls.gsheet = gsheet
      request.cls.email = email

      yield

      service.end()
      base.exit()

It has 5 decorators, which first, ``@pytest.fixture(scope="class")``, is used to set the scope of the exeception based on class. Meanwhile the remaining fixtures are implemented to use other fixtures which are defined in ``./_fixtures``.

Inside the function, it has 2 part as well, which are setup and teardown separated by yield. In the setup process, it defines instances, such as BaseDriver and DBService. Meanwhile in teardown, it shutdowns the service and driver.