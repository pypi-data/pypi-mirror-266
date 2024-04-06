import logging


class RootFilter(logging.Filter):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.name = name

    def filter(self, record: logging.LogRecord) -> bool:
        return record.name.startswith(self.name)


class Logger:
    """Logging messages for a specific system or application component"""

    def __init__(self) -> None:
        # instantiate logging components
        self.logger = logging.getLogger("root")
        self.file_handler = logging.FileHandler("automation.log", mode="w")
        # self.console_handler = logging.StreamHandler()
        self.formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")

        # set up
        self.setup()

    def setup(self):
        # set level of the logger
        self.logger.setLevel(logging.ERROR)

        # set level of the handler
        self.file_handler.setLevel(logging.ERROR)
        # self.console_handler.setLevel(logging.ERROR)

        # install formatter into the handlers
        self.file_handler.setFormatter(self.formatter)
        # self.console_handler.setFormatter(self.formatter)

        # add filters
        self.logger.addFilter(RootFilter(name=self.logger.name))
        self.file_handler.addFilter(RootFilter(name=self.logger.name))
        # self.console_handler.addFilter(RootFilter(name="root"))

        # add the handlers to the logger
        self.logger.addHandler(self.file_handler)
        # self.logger.addHandler(self.console_handler)

    def shutdown(self):
        logging.shutdown()
