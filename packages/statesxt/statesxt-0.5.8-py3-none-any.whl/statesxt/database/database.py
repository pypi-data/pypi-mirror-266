from sshtunnel import SSHTunnelForwarder
import psycopg2


class PostgreDB:
    """Root database"""

    def __init__(self, SSH_HOST, SSH_PORT, SSH_USERNAME, SSH_PASSWORD, DB_SERVER, DB_PORT) -> None:
        self.__SSH_HOST = SSH_HOST
        self.__SSH_PORT = int(SSH_PORT)
        self.__SSH_USERNAME = SSH_USERNAME
        self.__SSH_PASSWORD = SSH_PASSWORD
        self.__DB_SERVER = DB_SERVER
        self.__DB_PORT = int(DB_PORT)
        self.__DB_NAME = ""
        self.__DB_USER = ""
        self.__DB_PASSWORD = ""

    """GETTERS"""

    @property
    def SSH_HOST(self):
        return self.__SSH_HOST

    @property
    def SSH_PORT(self):
        return self.__SSH_PORT

    @property
    def SSH_USERNAME(self):
        return self.__SSH_USERNAME

    @property
    def SSH_PASSWORD(self):
        return self.__SSH_PASSWORD

    @property
    def DB_SERVER(self):
        return self.__DB_SERVER

    @property
    def DB_PORT(self):
        return self.__DB_PORT

    @property
    def DB_NAME(self):
        return self.__DB_NAME

    @property
    def DB_USER(self):
        return self.__DB_USER

    @property
    def DB_PASSWORD(self):
        return self.__DB_PASSWORD

    def connect(self):
        try:
            with SSHTunnelForwarder(
                (self.SSH_HOST, self.SSH_PORT),
                ssh_username=self.SSH_USERNAME,
                ssh_password=self.SSH_PASSWORD,
                remote_bind_address=(self.DB_SERVER, self.DB_PORT),
                local_bind_address=("xxx.x.x.x", 0),
            ) as server:
                server.start()
                params = {
                    "database": self.DB_NAME,
                    "user": self.DB_USER,
                    "password": self.DB_PASSWORD,
                    # "host": self.DB_SERVER,
                    "host": "127.0.0.1",
                    # "port": self.DB_PORT,
                    "port": server.local_bind_port,
                }
                self.conn = psycopg2.connect(**params)
                self.cursor = self.conn.cursor()

        except Exception as e:
            print(f"\n\nerror message: {str(e)}\n\n")
            print(str(e))
            raise Exception("Connection Failed")

    def disconnect(self):
        self.conn.close()

    def query_read(self, query):
        try:
            self.cursor.execute(query)
            column_names = [desc[0] for desc in self.cursor.description]
            rows = self.cursor.fetchall()
            results = []
            for row in rows:
                result = dict(zip(column_names, row))
                results.append(result)
            return results
        except Exception as e:
            self.conn.rollback()
            raise ConnectionError(str(e))

    def query_add_edit(self, query):
        self.cursor.execute(query)
        self.conn.commit()
        return self.cursor.rowcount


class ExampleDB(PostgreDB):
    """Example database"""

    def __init__(
        self,
        DB_NAME,
        DB_USER,
        DB_PASSWORD,
        SSH_HOST,
        SSH_PORT,
        SSH_USERNAME,
        SSH_PASSWORD,
        DB_SERVER,
        DB_PORT,
    ) -> None:
        super().__init__(SSH_HOST, SSH_PORT, SSH_USERNAME, SSH_PASSWORD, DB_SERVER, DB_PORT)
        self.__DB_NAME = DB_NAME
        self.__DB_USER = DB_USER
        self.__DB_PASSWORD = DB_PASSWORD

    """GETTERS"""

    @property
    def DB_NAME(self):
        return self.__DB_NAME

    @property
    def DB_USER(self):
        return self.__DB_USER

    @property
    def DB_PASSWORD(self):
        return self.__DB_PASSWORD
