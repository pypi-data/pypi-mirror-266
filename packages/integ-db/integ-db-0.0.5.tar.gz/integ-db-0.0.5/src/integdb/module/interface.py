class SessionConfig():
    def __init__(self, host, user, password, port, schema, connection_pool):
        self._host = host
        self._user = user
        self._password = password
        self._port = int(port)
        self._schema = schema
        self._conn = None
        self._engine = None
        self._connection_str = None
        self._pool = None
        self._ispool = connection_pool

class DefaultInterface(SessionConfig):
    def __init__(self, host, user, password, port, schema, connection_pool):
        super().__init__(host, user, password, port, schema, connection_pool)

    def _getcursor(self):
        if self._ispool:
            pconn = self._pool.get_connection()
            return pconn, pconn.cursor()
        else:
            return self._conn, self._conn.cursor()
        
    def sql_executer_commit(self, sql_context):
        conn, cursor = self._getcursor()

        try:
            cursor.execute(sql_context)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise Exception(e)
        finally:
            cursor.close()

    def sql_executer_many_commit(self, sql_context, rows):
        conn, cursor = self._getcursor()

        try:
            cursor.executemany(sql_context, rows)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise Exception(e)
        finally:
            cursor.close()

    def sql_executer(self, sql_context):
        def __dictfetchall(cursor):
            desc = cursor.description 
            return [
                dict(zip([col[0] for col in desc], row)) 
                for row in cursor.fetchall() 
            ]
        conn, cursor = self._getcursor()

        try:
            cursor.execute(sql_context)
            rows = __dictfetchall(cursor)
            conn.commit()
            return rows
        except Exception as e:
            raise Exception(e)
        finally:
            cursor.close()

    def sql_callproc(self, procname: str, *arg):
        conn, cursor = self._getcursor()

        try:
            cursor.callproc(procname, arg)
            conn.commit()
        except Exception as e:
            raise Exception(e)
        finally:
            cursor.close()