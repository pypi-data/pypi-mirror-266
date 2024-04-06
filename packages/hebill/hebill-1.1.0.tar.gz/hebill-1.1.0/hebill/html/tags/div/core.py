from ...nodes import Tag


class Div(Tag):
    def __init__(self, senior, text: str = None):
        super().__init__(senior, 'div')
        if text is not None:
            self.create.node.content(text)
