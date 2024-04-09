from ...nodes import Tag


class Tr(Tag):
    def __init__(self, senior):
        super().__init__(senior, 'tr')
        