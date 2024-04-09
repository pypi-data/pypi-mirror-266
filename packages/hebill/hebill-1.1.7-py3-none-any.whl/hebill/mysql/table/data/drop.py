from ...datatable import datatable as datatable_class
from hebill.modules.mysql.plugins import wheres as wheres_class, limits as limits_class, orders as orders_class


class drop:
    def __init__(self, datatable: datatable_class):
        self._datatable = datatable
        self.query = datatable.query
        self.prefix = datatable.prefix
        self.logger = datatable.logger
        self._wheres = None
        self._orders = None
        self._limits = None

    def wheres(self) -> wheres_class:
        if self._wheres is None:
            self._wheres = wheres_class()
        return self._wheres

    def orders(self) -> orders_class:
        if self._orders is None:
            self._orders = orders_class()
        return self._orders

    def limits(self) -> limits_class:
        if self._limits is None:
            self._limits = limits_class()
        return self._limits

    def all(self):
        sql = f'DELETE FROM {self._datatable.real_name}'
        ero = f'删除所有数据表{self._datatable.name}全部数据发生错误：{{e}}'
        return self.query(sql, ero)[1]

    def single(self):
        self.limits().set_limits(0, 1)
        sql = f'DELETE FROM `{self._datatable.real_name}` ' + self.wheres().output() + self.limits().output()
        ero = f'删除数据表{self._datatable.name}单条数据发生错误：{{e}}'
        return self.query(sql, ero)[1]

    def multiple(self):
        sql = f'DELETE FROM `{self._datatable.real_name}` ' + self.wheres().output() + self.limits().output()
        ero = f'删除数据表{self._datatable.name}单(多)条数据发生错误：{{e}}'
        return self.query(sql, ero)[1]
