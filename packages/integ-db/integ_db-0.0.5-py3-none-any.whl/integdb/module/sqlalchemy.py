import pandas as pd
from sqlalchemy import create_engine
from module.interface import SessionConfig
from sqlalchemy.exc import IntegrityError

class SQLAlchemy(SessionConfig):
    def __init__(self, host, user, password, port, schema, connection_pool):
        super().__init__(host, user, password, port, schema, connection_pool)

    def connect(self, db_url="mysql+pymysql"):
        try:
            self._connection_str = f'{db_url}://{self._user}:{self._password}@{self._host}:{self._port}/{self._schema}'
            self._engine = create_engine(url=self._connection_str)
        except Exception as e:
            raise Exception(f'Error connecting to the SQLAlchemy: {e}')
        
    def close(self):
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None

    def sql_export(self, df: pd.DataFrame, name, schema=None):
        try:
            if self._engine is None:
                self._engine = create_engine(url=self._connection_str)

            db_schema = self._schema
            if schema is not None:
                db_schema = schema
            df.to_sql(name, con=self._engine, if_exists='append', index=False, schema=db_schema)
        except IntegrityError as e:
            raise IntegrityError(e.statement, e.params, e.orig)
        except Exception as e:
            raise Exception(e)

    def sql_to_pandas(self, sql_context):
        try:
            if self._engine is None:
                self._engine = create_engine(url=self._connection_str)

            df_rows = pd.read_sql(sql_context, con=self._engine)
            return df_rows
        except IntegrityError as e:
            raise IntegrityError(e.statement, e.params, e.orig)
        except Exception as e:
            raise Exception(e)