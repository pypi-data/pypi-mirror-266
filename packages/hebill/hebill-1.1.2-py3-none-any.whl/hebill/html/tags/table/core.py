from ...nodes import Tag


class Table(Tag):
    def __init__(self, senior):
        super().__init__(senior, 'table')
