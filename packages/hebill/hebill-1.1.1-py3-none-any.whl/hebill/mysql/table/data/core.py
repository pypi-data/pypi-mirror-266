class Data:
    def __init__(self, table):
        self._table = table

    @property
    def drop(self):
        from .data_sub.drop import drop
        return drop(self._datatable)

    @property
    def insert(self):
        from .data_sub.insert import insert
        return insert(self._datatable)

    @property
    def search(self):
        from .data_sub.search import search
        return search(self._datatable)

    @property
    def update(self):
        from .data_sub.update import update
        return update(self._datatable)

