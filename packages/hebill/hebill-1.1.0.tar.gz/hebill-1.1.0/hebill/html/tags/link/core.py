from ...nodes import Tag


class Link(Tag):
    def __init__(self, senior, url: str = None):
        super().__init__(senior, 'link')
        if url is not None:
            self.attributes["href"] = url
