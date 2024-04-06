from ....tags.thead.core import Thead as TheadParentClass
from .tr.core import Tr


class Thead(TheadParentClass):
    def __init__(self, senior):
        super().__init__(senior)
        self._rows = []
        self._row = None

    @property
    def rows(self) -> list:
        return self._rows

    @property
    def row(self) -> Tr:
        if self._row is None:
            self.add_row()
        return self._row

    def add_row(self) -> Tr:
        self._row = Tr(self)
        self._rows.append(self._row)
        return self._row
