#########
/locators
#########

A locator is a way to identify and locate a specific element on a web page so that actions can be performed on it programmatically. Locators are crucial for automated testing and web scraping.

The main function of this folder is to store all variables that each contains an unique identifier to a web element.


__init__.py
===========
For this dunder init file, besides its function to recognize the directory, in this case is ``/locators``, as a Python package, it also defines a ``Locator`` class, which will be the parent class of all specific page locator classes.

.. code-block:: python
    
    class Locator:
        """A parent class of all page locators."""

        def __init__(self, base: BaseDriver) -> None:
            self.__bd = base
            self.by = MyBy()

        @property
        def bd(self):
            return self.__bd

``Locator`` class has 2 attributes, ``self.__bd = base``, that is a composition object of ``BaseDriver``, and ``self.by = MyBy()`` that is also an implementation of composition relationship. Besides attributes, there is also a method used as a getter to retrieve the value of ``self.__bd`` attribute. 


example_locator.py
==================
Is an example of a page locator. In this class, you will define all of your web element identifiers based on page. You can use this example as reference.

.. code-block:: python

    class ExampleLocator(Locator):
        """Example page locator class"""

        def __init__(self, base) -> None:
            super().__init__(base)
            self.setup()

        def setup(self):
            # main components
            self.EXAMPLE_BUTTON = lambda loc="//button[@data-rr-ui-event-key='example']": self.bd.wd.clickable(self.by.xpath, loc)

            # flags
            self.JPN_FLAG_BUTTON = lambda loc="//div[@class='d-flex justify-content-center']//label[1]": self.bd.wd.clickable(self.by.xpath, loc)
            self.ENG_FLAG_BUTTON = lambda loc="//div[@class='d-flex justify-content-center']//label[2]": self.bd.wd.clickable(self.by.xpath, loc)

The class does not have any attribute variables defined, instead it has a ``super().__init__(base)``, which an inheritance stuff, and ``self.setup()`` to invoke the method that is responsible for variables definition at execution. 

These are several things about the variable definition in ``setup()`` method,

* It uses lambda function mainly for code simplicity,
* Each function has one parameter that you need to define, which is ``loc``, that is used to store the web element identifier for later be used inside the function,
* At first, the lambda functions are only being defined and are stored inside variables, meaning that it has not been executed yet. Therefore you need to add ``()`` for the suffix when invoking the variables, e.g. ``self.EXAMPLE_BUTTON()``.