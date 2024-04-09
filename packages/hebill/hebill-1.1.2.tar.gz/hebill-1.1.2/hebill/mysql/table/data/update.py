from ...table import Table
from ...plugins import Wheres


class Update:
    def __init__(self, table: Table):
        self._table = table
        self._wheres = None

    @property
    def table(self): return self._table

    @property
    def wheres(self) -> Wheres:
        if self._wheres is None:
            self._wheres = Wheres()
        return self._wheres

    def multiple(self, data=None):
        if not data:
            return False

        str_array = [f'`{key}` = "{value}"' for key, value in data.items()]
        query = f"UPDATE `{self.table.fullname}` SET {', '.join(str_array)}{self.wheres.output()}"
        result = self.table.query(query)[1]
        return bool(result)
