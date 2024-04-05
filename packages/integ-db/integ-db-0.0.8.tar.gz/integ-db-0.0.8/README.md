# integdb
### This package Integrated Database library, based on PyMySQL, pymssql, mariadb, SQLAlchemy.

#### Requirements
- MySQL
- MSSQL(SQL Server)
- MariaDB

#### Controller Object
- MySQL
- MariaDB
- MSSQL
- SQLAlchemy

#### Object that provides a pool
- MySQL
- MariaDB

## Install
#### From PIP
```
pip install integ-db
```
## Example
```
from integdb import Controller

host = "localhost"
user = "usrname"
password = "password"
port = 3306
schema = "database_name"
controller = Controller(
                    host=host,
                    user=user,
                    password=password,
                    port=port,
                    schema=schema,
                    connection_pool=False)
try:
    controller.MySQL.connect()
    sql_context = "SELECT * FROM TEST_DB"
    rows = controller.MySQL.sql_executer(sql_context)
    print (rows)
except Exception as e:
    print (e)
finally:
    controller.MySQL.close()
```