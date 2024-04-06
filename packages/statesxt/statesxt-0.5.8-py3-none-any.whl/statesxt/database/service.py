from database.database import ExampleDB
from database.queries import Query
from utils.formatter import Formatter
import os


class DBService:
    """Database service"""

    def __init__(self) -> None:
        self.setup()

        self.__query = Query()
        self.ft = Formatter()

    def setup(self):
        SSH_HOST = os.getenv("POSTGRE_DB_SSH_HOST")
        SSH_PORT = os.getenv("POSTGRE_DB_SSH_PORT")
        SSH_USERNAME = os.getenv("POSTGRE_DB_SSH_USERNAME")
        SSH_PASSWORD = os.getenv("POSTGRE_DB_SSH_PASSWORD")
        DB_SERVER = os.getenv("POSTGRE_DB_DB_SERVER")
        DB_PORT = os.getenv("POSTGRE_DB_DB_PORT")
        EXAMPLE_DB_NAME = os.getenv("EXAMPLE_DB_DB_NAME")
        EXAMPLE_DB_USER = os.getenv("EXAMPLE_DB_DB_USER")
        EXAMPLE_DB_PASSWORD = os.getenv("EXAMPLE_DB_DB_PASSWORD")
        self.__exampleDB = ExampleDB(
            DB_NAME=EXAMPLE_DB_NAME,
            DB_USER=EXAMPLE_DB_USER,
            DB_PASSWORD=EXAMPLE_DB_PASSWORD,
            SSH_HOST=SSH_HOST,
            SSH_PORT=SSH_PORT,
            SSH_USERNAME=SSH_USERNAME,
            SSH_PASSWORD=SSH_PASSWORD,
            DB_SERVER=DB_SERVER,
            DB_PORT=DB_PORT,
        )

    def start(self):
        self.__exampleDB.connect()

    def end(self):
        self.__exampleDB.disconnect()

    # example page
    def get_all_examples(self):
        qResult = self.__exampleDB.query_read(self.__query.__GET_ALL_EXAMPLES)
        return self.ft.convert_query_result(
            query_result=qResult,
            rounding_columns=[],
            rounding_option=1,
        )
