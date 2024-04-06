from ...tags.table.core import Table as TableParentClass
from .thead.core import Thead
from .tbody.core import Tbody


class Table(TableParentClass):
    def __init__(self, senior):
        super().__init__(senior)
        self._head_wrap = self.create.node.group()
        self._head = None
        self._body = None

    @property
    def head(self) -> Thead:
        if self._head is None:
            self._head = Thead(self._head_wrap)
        return self._head

    @property
    def body(self) -> Tbody:
        if self._body is None:
            self._body = Tbody(self)
        return self._body

    def set_bordered(self):
        pass
