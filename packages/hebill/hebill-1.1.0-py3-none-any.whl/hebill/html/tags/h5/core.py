from ...nodes import Tag


class H5(Tag):
    def __init__(self, senior, text: str = None):
        super().__init__(senior, 'h5')
        if text is not None:
            self.create.node.content(text)
