from ...nodes import Tag


class H1(Tag):
    def __init__(self, senior, text: str = None):
        super().__init__(senior, 'h1')
        if text is not None:
            self.create.node.content(text)
