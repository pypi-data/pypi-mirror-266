import pymysql
import pymysql.cursors
from dbutils.pooled_db import PooledDB
from .constants import SQL_MAX_CONNECTIONS, SQL_CONNECT_TIMEOUT, SQL_CHARSET


class Database:
    def __init__(self, host: str, user: str, password: str, name: str, port: int = 3306, prefix=''):
        self._host = host
        self._user = user
        self._password = password
        self._name = name
        self._port = port
        self._prefix = prefix
        self._pool = None
        self._queried: str = ''
        self._error: str = ''

    @property
    def pool(self):
        if self._pool is None:
            self._pool = PooledDB(
                creator=pymysql,
                maxconnections=SQL_MAX_CONNECTIONS,
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database=self.name,
                charset=SQL_CHARSET,
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=SQL_CONNECT_TIMEOUT
            )
        return self._pool

    def query(self, sql, action: str = None):
        self._queried = sql
        try:
            with self.pool.connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    connection.commit()
                    match action:
                        case 'data':
                            r = cursor.fetchall()
                            return r if r else []
                        case 'insert':
                            if cursor.lastrowid > 0:
                                return cursor.lastrowid
                            else:
                                cursor.execute("SELECT LAST_INSERT_ID()")
                                return cursor.fetchone()[0]
                        case 'quantity':
                            return cursor.fetchone().get('COUNT(*)')
        except Exception as e:
            self._error = e

        finally:
            if connection:
                connection.close()
        return None

    @property
    def host(self): return self._host

    @property
    def name(self): return self._name

    @property
    def user(self) -> str: return self._user

    @property
    def password(self) -> str: return self._password

    @property
    def port(self) -> int: return self._port

    @property
    def prefix(self): return self._prefix

    @property
    def table_names(self) -> list:
        result = self.query('SHOW TABLES', 'data')
        datatables = []
        if result is not None:
            datatables = [table[f'Tables_in_{self._name}'] for table in result]
        return datatables

    def create_table(self, name) -> bool:
        sql = (f'CREATE TABLE IF NOT EXISTS `{self.prefix}{name}` ('
               f'`_id` bigint NOT NULL AUTO_INCREMENT,'
               f'`_sn` varchar(64) NOT NULL,'
               f'`_order` bigint NOT NULL,'
               f'`_keywords` text NOT NULL,'
               f'`_created_by` bigint NOT NULL,'
               f'`_created_date` bigint NOT NULL,'
               f'PRIMARY KEY (`_id`)'
               f') ENGINE=InnoDB DEFAULT CHARACTER SET=utf8 COLLATE=utf8_unicode_ci')
        return self.query(sql)

    def delete_table(self, name: str) -> bool:
        return self.query(f'DROP TABLE IF EXISTS `{self.prefix}{name}`')

    def is_table_exist(self, name: str) -> bool:
        result = self.query(f"SHOW TABLES LIKE '{self.prefix}{name}'", 'data')[1]
        return len(result) > 0

    def table(self, name: str):
        from .table.core import Table
        return Table(self, name)
