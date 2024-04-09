from ...nodes import Tag


class H4(Tag):
    def __init__(self, senior, text: str = None):
        super().__init__(senior, 'h4')
        if text is not None:
            self.create.node.content(text)
