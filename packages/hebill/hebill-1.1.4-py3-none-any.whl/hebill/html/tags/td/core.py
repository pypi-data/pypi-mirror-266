from ...nodes import Tag


class Td(Tag):
    def __init__(self, senior, text: str = None):
        super().__init__(senior, 'td')
        if text is not None:
            self.create.node.content(text)
        