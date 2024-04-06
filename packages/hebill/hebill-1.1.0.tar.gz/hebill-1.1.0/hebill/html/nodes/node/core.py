class Node:
    def __init__(self, sir):
        self._id = id(self)
        from ...core import Document
        self._document: Document
        from ..group.core import Group
        self._senior: Group | None = None
        if isinstance(sir, Document):
            self._document = sir
        elif isinstance(sir, Group):
            self._senior = sir
            self._document = sir.document
            self.senior.local_add_junior(self)
        self.document.local_add_element(self)
        self.output_breakable = False

    @property
    def id(self): return self._id

    @property
    def document(self): return self._document

    @property
    def senior(self): return self._senior

    @property
    def level(self) -> int:
        if self._senior is None:
            return 0
        from ...nodes.tag.core import Tag
        from ...nodes.group.core import Group
        if isinstance(self, Group) and not isinstance(self, Tag):
            return self.senior.level
        return self.senior.level + 1

    def output(self) -> str:
        pass
