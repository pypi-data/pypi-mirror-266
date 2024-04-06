from functools import wraps
import logging
import sys
from selenium.common.exceptions import StaleElementReferenceException
from .faker import FakerGenerator
import time as t


class Wrapper:
    """Making use functools\wraps"""

    @classmethod
    def exception_handling_returns_None(cls, func):
        """
        to let a test case returns a None value instead of raises an exception/error
        """
        decoratorClassName = cls.__name__
        decoratorMethodName = sys._getframe().f_code.co_name

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.getLogger(f"root.{__name__}.{decoratorClassName}.{decoratorMethodName}").error(f"error:\n{str(e)}")
                return None

        return wrapper

    @classmethod
    def exception_handling_raises_error(cls, func):
        """
        to handle the error by tracking, but keeps raises the error
        """
        decoratorClassName = cls.__name__
        decoratorMethodName = sys._getframe().f_code.co_name

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.getLogger(f"root.{__name__}.{decoratorClassName}.{decoratorMethodName}").error(f"error:\n{str(e)}")
                raise Exception(str(e))

        return wrapper

    @classmethod
    def stale_handler(func):
        """
        forced a function to retry find a missing staled element
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except StaleElementReferenceException:
                t.sleep(1.8)
                return func(*args, **kwargs)

        return wrapper

    @classmethod
    def result_receiving(cls, func):
        """
        to track the result of test cases, so instead of directly raising error, it lets to write down the error first, e.g. email, report, and summary
        """
        decoratorClassName = cls.__name__
        decoratorMethodName = sys._getframe().f_code.co_name

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            funcName = str(func.__name__).replace("_", " ").title()
            className = self.__class__.__name__
            isFail = False

            try:
                func(self, *args, **kwargs)
                self.store.setScenarioResult(className, funcName, "PASSED")
            except Exception as e:
                if str(e).replace("'", "") != funcName:
                    logging.getLogger(f"root.{__name__}.{decoratorClassName}.{decoratorMethodName}").error(f"class: {self.__class__.__name__}, method: {func.__name__}\n{str(e)}")
                self.store.setScenarioResult(className, funcName, "FAILED")
                errorMsg = str(e)
                isFail = True

            self.store.printUseCaseResults(className)
            self.store.updateJSON()
            if isFail:
                raise Exception(errorMsg)

        return wrapper

    @classmethod
    def unpagshe(cls, worksheet, named_range, needExternalCheck=False):
        """
        to retrieve and unpack the data from gsheet
        """
        decoratorClassName = cls.__name__
        decoratorMethodName = sys._getframe().f_code.co_name

        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                data = self.sa.get_values_by_named_range(worksheet, named_range)
                result = []
                isFail = False
                emptyFormats = [
                    "",
                    "-",
                    "<blank>",
                    "<empty>",
                    "blank",
                    "empty",
                    "inactive",
                    "uncheck",
                ]
                anyFormats = ["anything", "dc", "Any", "any"]

                for row in data:
                    # preprocess data
                    row = [None if (col in emptyFormats) else col for col in row]
                    row = [(FakerGenerator().generate_sentence() if (col in anyFormats) else col) for col in row]

                    try:
                        func(self, *row, *args, **kwargs)
                        result.append(["PASSED", "PASSED" if needExternalCheck else "", ""])
                        self.p.resetState()
                    except Exception as e:
                        logging.getLogger(f"root.{__name__}.{decoratorClassName}.{decoratorMethodName}").error(
                            f"class: {self.__class__.__name__}, method: {func.__name__}\n{str(e)}"
                        )
                        # raise Exception(str(e))
                        result.append(["FAILED", "FAILED" if needExternalCheck else "", f"'{str(e)}'"])
                        errorMsg = str(e)
                        isFail = True

                self.store.setTestCasesResult(worksheet, named_range, result)
                if isFail:
                    raise Exception(errorMsg)

            return wrapper

        return decorator
