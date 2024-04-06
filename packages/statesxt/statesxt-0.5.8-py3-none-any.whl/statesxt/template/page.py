from .. import Page, StateInterface as SI
from .states import *
from .locator import ExampleLocator
from .interface import ExampleInterface


class ExamplePage(Page):
    """Example Page action methods"""

    def __init__(self, base, usecase):
        super().__init__(base)
        self.initState: ExampleInterface = self.setInitState(usecase)
        self.state = self.initState
        self.lr = ExampleLocator(base)

    def setInitState(self, usecase):
        dict = {
            1: ExampleInitState(self.bd, self),
        }
        return dict[usecase]

    """
    Method: Abstracts
    """

    # region
    def changeState(self, newState):
        self.state = newState

    def resetState(self):
        self.state = self.initState

    # endregion

    """
    Method: Interfaces
    """

    # region ==> is a Python feature to freely collapsing code, ended with endregion
    @SI.updateParam
    def simpleTransition(self, simpleParam):
        return self.state.simpleTransition()

    # endregion

    """
    Method: Specifics
    """
    # region
    # endregion
