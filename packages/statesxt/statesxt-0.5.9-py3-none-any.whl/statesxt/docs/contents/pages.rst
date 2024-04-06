######
/pages
######

This folder contains other things related to pages, e.g. definition of transitions and methods whose scope is limited to pages only.


__init__.py
===========
For this dunder init file, besides its function to recognize the directory, in this case is ``/pages``, as a Python package, it also defines a ``Page`` class, which will be the parent class of all specific page classes.

.. code-block:: python

    class Page(ABC):
        def __init__(self, base: BaseDriver) -> None:
            self.__bd = base
            self.jpnFormats = ["jpn", "japan", "japanese", "jp"]
            self.engFormats = ["eng", "english", "en"]
            self.emptyFormats = ["", "-", "<blank>", "<empty>", "blank", "empty"]
            self.anyFormats = ["anything", "dc", "Any", "any"]
            self.spaceFormats = ["<space>"]

        @property
        def bd(self):
            return self.__bd

        @abstractmethod
        def changeState(self):
            pass

As above, the ``Page`` class has a number of attributes, but actually the crucial one is only the ``self.__bd = base`` that defines the ``BaseDriver`` composition object, which can be retrieved through ``bd()`` method property. This is used so the value of the ``bd`` will remain consistent since it can not be changed from outside the class.

The other attributes are defined only for the purpose of variables centralization, so it avoids our code becoming repetitive. 

Besides ``bd()``, there is another method called ``changeState()``, which is an ``abstractmethod``, meaning it is required to all the childs of this class to define it. This method is also the implementation of State Design Pattern, which is used to change current state to a new state.


example_page.py
===============
Is an example of a specific page class. These classes are considered as the Context in State Design Pattern. If you have already read about `the pattern <https://refactoring.guru/design-patterns/state>`_, then you probably already familiar with it. 

.. code-block:: python

    class ExamplePage(Page):
        """Example Page action methods"""

        def __init__(self, base):
            super().__init__(base)
            self.lr = ExampleLocator(base)

Other than the ``super().__init__(base)`` that inherits the methods and attributes of the parent ``Page`` class, it also has a ``self.lr = ExampleLocator(base)`` so that a page has access to its locators.

.. code-block:: python

    # Interface Methods
    def changeState(self, newState):
        self.state = newState

    def clickLogin(self, *args, **kwargs):
        return self.state.clickLogin(*args, **kwargs)

    def changeLanguage(self, *args, **kwargs):
        return self.state.changeLanguage(*args, **kwargs)

    def success(self, *args, **kwargs):
        return self.state.success(*args, **kwargs)

    def error(self, *args, **kwargs):
        return self.state.error(*args, **kwargs)

Besides the ``changeState()`` that has been introduced before, the others are some examples of interface methods. These methods will be invoked from test scenarios, which later the other similar methods will also be invoked as well, i.e. in ``/testcases/_interfaces`` and ``/testcases/_states``.

As a ``Context`` class, this page specific class does not need to know the specific details of how each state handles requests; it relies on the common interface defined by the ``State`` class.