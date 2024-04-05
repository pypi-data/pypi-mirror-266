import mariadb
from .interface import DefaultInterface

class MariaDB(DefaultInterface):
    def connect(self, pool_name="app-pool", pool_size=20):
        try:
            if self._ispool is False:
                self._conn = mariadb.connect(
                    host=self._host,
                    user=self._user,
                    password=self._password,
                    port=self._port,
                    database=self._schema)
            else:
                self._pool = mariadb.ConnectionPool(
                    host=self._host,
                    user=self._user,
                    password=self._password,
                    port=self._port,
                    pool_name=pool_name,
                    pool_size=pool_size)
        except Exception as e:
            raise Exception(f'Error connecting to the MariaDB: {e}')
        
    def close(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def set_auto_reconnect(self, auto):
        self._conn.auto_reconnect = auto