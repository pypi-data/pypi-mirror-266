from ..interface import ExampleInterface


class ExampleInitState(ExampleInterface):
    def __init__(self, base, contextPage) -> None:
        super().__init__(base, contextPage)

    def simpleTransition(self):
        """Required Process"""
        self.bd.fd.insert_to_textbox(self.p.lr.SIMPLE_LOCATOR1(), self.param["simpleParam"])
        """Transition"""
        self.p.changeState(ExampleInitState(self.bd, self.p))
