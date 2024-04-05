from .module.mysql import MySQL
from .module.mssql import MSSQL
from .module.mariadb import MariaDB
from .module.sqlalchemy import SQLAlchemy

class Controller():
    def __init__(self, host, user, password, port, schema, connection_pool=False):
        self.MySQL = MySQL(host, user, password, port, schema, connection_pool)
        self.MaridDB = MariaDB(host, user, password, port, schema, connection_pool)
        self.MSSQL = MSSQL(host, user, password, port, schema, connection_pool)
        self.SQLAlchemy = SQLAlchemy(host, user, password, port, schema, connection_pool)
        