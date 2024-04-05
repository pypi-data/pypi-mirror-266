from module import MySQL
from module import MSSQL
from module import MariaDB
from module import SQLAlchemy

class Controller():
    def __init__(self, host, user, password, port, schema, connection_pool=False):
        self.MySQL = MySQL(host, user, password, port, schema, connection_pool)
        self.MaridDB = MariaDB(host, user, password, port, schema, connection_pool)
        self.MSSQL = MSSQL(host, user, password, port, schema, connection_pool)
        self.SQLAlchemy = SQLAlchemy(host, user, password, port, schema, connection_pool)
        