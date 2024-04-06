from ...nodes import Tag


class H3(Tag):
    def __init__(self, senior, text: str = None):
        super().__init__(senior, 'h3')
        if text is not None:
            self.create.node.content(text)
