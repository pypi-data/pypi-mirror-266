from .....tags.tr.core import Tr as TrParentClass
from .td.core import Td


class Tr(TrParentClass):
    def __init__(self, senior):
        super().__init__(senior)
        self._cells = []
        self._cell = None

    @property
    def cells(self) -> list:
        return self._cells

    @property
    def cell(self) -> Td:
        if self._cell is None:
            self.add_cell()
        return self._cell

    def add_cell(self, text: str = None) -> Td:
        self._cell = Td(self, text)
        self._cells.append(self._cell)
        return self._cell
