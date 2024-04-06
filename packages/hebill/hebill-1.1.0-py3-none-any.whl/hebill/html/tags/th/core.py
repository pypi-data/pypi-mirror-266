from ...nodes import Tag


class Th(Tag):
    def __init__(self, senior, text: str = None):
        super().__init__(senior, 'th')
        if text is not None:
            self.create.node.content(text)
        