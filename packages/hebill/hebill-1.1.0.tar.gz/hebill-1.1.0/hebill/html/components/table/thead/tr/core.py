from .....tags.tr.core import Tr as TrParentClass
from .th.core import Th


class Tr(TrParentClass):
    def __init__(self, senior):
        super().__init__(senior)
        self._cells = []
        self._cell = None

    @property
    def cells(self) -> list:
        return self._cells

    @property
    def cell(self) -> Th:
        if self._cell is None:
            self.add_cell()
        return self._cell

    def add_cell(self, text: str = None) -> Th:
        self._cell = Th(self, text)
        self._cells.append(self._cell)
        return self._cell
