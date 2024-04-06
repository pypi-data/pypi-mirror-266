from ...nodes import Tag


class Script(Tag):
    def __init__(self, senior, url: str = None):
        super().__init__(senior, 'script')
        if url is not None:
            self.attributes["src"] = url
