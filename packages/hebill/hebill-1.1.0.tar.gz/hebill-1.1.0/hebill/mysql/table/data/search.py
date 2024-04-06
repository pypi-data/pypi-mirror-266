from ...datatable import datatable as datatable_class
from hebill.modules.mysql.plugins import columns as columns_class, limits as limits_class, orders as orders_class, \
    wheres as wheres_class


class search:
    def __init__(self, datatable: datatable_class):
        self._datatable = datatable
        self.query = datatable.query
        self.prefix = datatable.prefix
        self.logger = datatable.logger
        self._wheres = None
        self._orders = None
        self._limits = None
        self._columns = None

    def wheres(self) -> wheres_class:
        if self._wheres is None:
            self._wheres = wheres_class()
        return self._wheres

    def columns(self) -> columns_class:
        if self._columns is None:
            self._columns = columns_class()
        return self._columns

    def orders(self) -> orders_class:
        if self._orders is None:
            self._orders = orders_class()
        return self._orders

    def limits(self) -> limits_class:
        if self._limits is None:
            self._limits = limits_class()
        return self._limits

    def single(self) -> dict | None:
        self.limits().set_limits(0, 1)
        r = self.multiple()
        if len(r) < 1:
            return None
        return r[0]

    def multiple(self) -> list:
        sql = (
            f"SELECT {self.columns().output()} "
            f"FROM `{self._datatable.real_name}`"
            f"{self.wheres().output()}{self.orders().output()}{self.limits().output()}"
        )
        ero = f"检索数据表{self._datatable.real_name}数据发生错误：{{e}}"
        return self.query(sql, ero, 'data')[1]

    def quantity(self):
        sql = (f"SELECT COUNT(*) FROM `{self._datatable.real_name}`"
               f"{self.wheres().output()}{self.orders().output()}{self.limits().output()}")
        ero = f"检索数据表{self._datatable.real_name}数据数量发生错误：{{e}}"
        return self.query(sql, ero, 'quantity')[1]
