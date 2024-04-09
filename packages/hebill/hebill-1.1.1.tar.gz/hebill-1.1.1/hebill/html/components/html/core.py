from ...tags import Html as HtmlParentClass
from .head.core import Head
from .body.core import Body


class Html(HtmlParentClass):
    def __init__(self, senior, lang: str = None):
        super().__init__(senior, lang)
        self._head = Head(self)
        self._body = Body(self)

    @property
    def head(self):
        return self._head

    @property
    def body(self):
        return self._body
