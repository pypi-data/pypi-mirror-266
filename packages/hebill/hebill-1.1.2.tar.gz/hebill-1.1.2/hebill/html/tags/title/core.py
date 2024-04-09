from ...nodes import Tag


class Title(Tag):
    def __init__(self, senior, text: str = None):
        super().__init__(senior, 'title')
        self.output_break_inner = False
        self._content = self.create.node.content()
        if text is not None:
            self._content.text = text

    @property
    def content(self):
        return self._content
