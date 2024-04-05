import pymssql
from module.interface import DefaultInterface

class MSSQL(DefaultInterface):
    def connect(self):
        try:
            self._conn = pymssql.connect(
                host=self._host,
                user=self._user,
                password=self._password,
                port=self._port,
                database=self._schema,
                charset='utf8')
        except Exception as e:
            raise Exception(f'Error connecting to the MSSQL: {e}')
        
    def close(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None