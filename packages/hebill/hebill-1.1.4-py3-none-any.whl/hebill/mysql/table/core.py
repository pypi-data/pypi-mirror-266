from ..features import TableIndexData
from ..features import TableStatusData
from ..features import TableDescribeData


class Table:
    def __init__(self, database, name):
        from ..core import Database
        self._database: Database = database
        self._name = name
        self._fullname = self.prefix + name
        self._index_info = None
        self._status_info = None
        self._describe_info = None

    @property
    def name(self):
        return self._name

    @property
    def fullname(self):
        return self._name

    @property
    def database(self):
        return self._database

    @property
    def prefix(self):
        return self.database.prefix

    def reload(self):
        self._index_info = None
        self._status_info = None
        self._index_info = None

    @property
    def status_info(self):
        if self._status_info is None:
            self._status_info = TableStatusData(self.query(f'SHOW TABLE STATUS LIKE "{self.fullname}";', 'data')[0])
        return self._status_info

    @property
    def index_info(self):
        if self._index_info is None:
            self._index_info = {}
            reply = self.query(f'SHOW INDEX FROM {self.fullname};', 'data')
            for i in reply:
                self._index_info[i['Key_name']] = TableIndexData(i)
        return self._index_info

    def index_info_by_key(self, keyname: str) -> TableIndexData | None:
        return self.index_info.get(keyname)

    @property
    def describe_info(self):
        if self._describe_info is None:
            self._describe_info = {}
            reply = self.query(f'DESCRIBE {self.fullname};', 'data')
            for i in reply:
                self._describe_info[i['Field']] = TableDescribeData(i)
        return self._describe_info

    def describe_info_by_field(self, field: str) -> TableDescribeData | None:
        return self.describe_info.get(field)

    def query(self, sql, action: str = None):
        return self.database.query(sql, action)

    def is_exists(self):
        return self.database.is_table_exist(self.fullname)

    def delete(self):
        return self.database.delete_table(self.fullname)

    def create(self):
        return self.database.create_table(self.fullname)

    @property
    def data(self):
        from .data.core import Data
        return Data(self)

    @property
    def column_names(self) -> list:
        return list(self.describe_info.keys())

    def set_auto_increment(self, number: int = 1):
        if number <= 0:
            return False
        return self.query(f'ALTER TABLE {self.fullname} AUTO_INCREMENT = {number};', 'data')

    def set_column_unique(self, column_name: str, keyname: str = None):
        if keyname is None:
            keyname = column_name
        if self.is_column_exist(column_name):
            return False
        return self.query(f'ALTER TABLE `{self.fullname}` ADD CONSTRAINT `{keyname}` UNIQUE KEY `{column_name}')

    def unset_column_unique(self, column_name: str, keyname: str = None):
        if keyname is None:
            keyname = column_name
        if keyname not in self.index_info or self.index_info_by_key(keyname).Column_name != column_name:
            return False
        return self.query(f'ALTER TABLE `{self.fullname}` DROP INDEX `{keyname}`')

    def set_column_nullable(self, column_name: str):
        info = self.describe_info_by_field(column_name)
        if info is None:
            return False
        return self.query(f'ALTER TABLE `{self.fullname}` MODIFY `{column_name}` {info.Type} NULL')

    def unset_column_nullable(self, column_name: str):
        info = self.describe_info_by_field(column_name)
        if info is None:
            return False
        return self.query(f'ALTER TABLE `{self.fullname}` MODIFY `{column_name}` {info.Type} NOT NULL')

    def set_column_auto_increment(self, column_name: str, start_number: int = 1):
        info = self.describe_info_by_field(column_name)
        if info is None or (not info.is_type_big_int and not info.is_type_int):
            return False
        if not info.is_auto_increment:
            self.query(f'ALTER TABLE `{self.fullname}` MODIFY `{column_name}` {info.Type} AUTO_INCREMENT')
        if start_number > 1:
            self.query(f'ALTER TABLE `{self.fullname}` AUTO_INCREMENT = {start_number}')
        return True

    def unset_column_auto_increment(self, column_name: str):
        info = self.describe_info_by_field(column_name)
        if info is None or (not info.is_type_big_int and not info.is_type_int):
            return False
        return self.query(f'ALTER TABLE `{self.fullname}` MODIFY `{column_name}` {info.Type}')

    def create_column(self, name: str, datatype: str = 'VARCHAR', length: int = 0,
                      unique: bool = False, nullable: bool = False, auto_increment: bool | int = False) -> bool:
        type_mapping = {
            "VARCHAR": f"VARCHAR({length})" if length else "VARCHAR(255)",
            "CHAR": f"CHAR({length})" if length else "CHAR(255)",
            "INT": "INT",
            "BIGINT": "BIGINT",
            "SMALLINT": "SMALLINT",
            "TINYINT": "TINYINT",
        }
        if datatype.upper() not in type_mapping:
            return False
        sql = (f'ALTER TABLE `{self.fullname}`'
               f' ADD `{name}` {type_mapping[datatype.upper()]}'
               f' {"UNIQUE" if unique else ""}'
               f' {"NULL" if nullable else "NOT NULL"}')
        self.query(sql)
        if auto_increment:
            self.set_column_auto_increment(name, int(auto_increment))
        return True

    def create_column_varchar(self, name: str, unique: bool = False, nullable: bool = False):
        return self.create_column(name, 'VARCHAR', 0, unique, nullable)

    def create_column_char(self, name: str, unique: bool = False, nullable: bool = False):
        return self.create_column(name, 'CHAR', 0, unique, nullable)

    def create_column_int(self, name: str, unique: bool = False, nullable: bool = False,
                          auto_increment: bool | int = False):
        return self.create_column(name, 'INT', 0, unique, nullable, auto_increment)

    def create_column_big_int(self, name: str, unique: bool = False, nullable: bool = False,
                              auto_increment: bool | int = False):
        return self.create_column(name, 'BIGINT', 0, unique, nullable, auto_increment)

    def create_column_small_int(self, name: str, unique: bool = False, nullable: bool = False):
        return self.create_column(name, 'SMALLINT', 0, unique, nullable)

    def create_column_tiny_int(self, name: str, unique: bool = False, nullable: bool = False):
        return self.create_column(name, 'TINYINT', 0, unique, nullable)

    def delete_column(self, name: str) -> bool:
        return self.query(f'ALTER TABLE `{self.fullname}` DROP COLUMN `{name}`')

    def is_column_exist(self, name: str) -> bool:
        return self.index_info_by_key(name) is not None

    def empty_data(self):
        self.query(f'DELETE FROM {self.fullname}')
        self.set_auto_increment(1)
        return True
