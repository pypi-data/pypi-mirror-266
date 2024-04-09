class Document:
    def __init__(self):
        self._elements = {}
        from .components import Html
        self._html = Html(self)
        from .nodes.group.create.core import Create
        self._create = Create(self)

        self.titles: list = []
        self.title_delimiter: str = " > "
        self.output_break: bool = True
        self.output_retraction: str = "	"
        self.output_next_breakable: bool = True

    @property
    def elements(self): return self._elements

    def local_add_element(self, ele): self._elements[ele.id] = ele

    @property
    def html(self): return self._html

    def create(self): return self._create

    def output(self) -> str:
        if len(self.titles) > 0:
            self.html.head.title.content.text = self.title_delimiter.join(self.titles)
        s = "<!DOCTYPE html>"
        if self.output_break:
            s += "\n"
        s += self.html.output()
        return s
