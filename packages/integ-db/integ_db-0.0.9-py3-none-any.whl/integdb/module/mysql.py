import pymysql
from pymysqlpool import ConnectionPool
from .interface import DefaultInterface

pymysql.install_as_MySQLdb()

class MySQL(DefaultInterface):
    def connect(self, pool_size=10):
        try:
            if self._ispool is False:
                self._conn = pymysql.connect(
                    host=self._host,
                    user=self._user,
                    password=self._password,
                    port=self._port,
                    db=self._schema,
                    charset='utf8')
            else:
                self.config = {
                    "host": self._host,
                    "user": self._user,
                    "port": self._port,
                    "password": self._password,
                    "database": self._schema
                }
                self._pool = ConnectionPool(size=pool_size, **self.config)
        except Exception as e:
            raise Exception(f'Error connecting to the MySQL: {e}')
        
    def close(self):
        if self._conn is not None and self._ispool is False:
            self._conn.close()
            self._conn = None