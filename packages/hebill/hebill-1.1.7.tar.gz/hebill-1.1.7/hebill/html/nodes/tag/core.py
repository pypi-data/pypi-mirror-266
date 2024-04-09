from ..group.core import Group


class Tag(Group):
    def __init__(self, sir, tag):
        super().__init__(sir)
        self._tag = tag
        from .attributes.core import Attributes
        self._attributes = Attributes()
        self.output_breakable = True

    @property
    def tag(self): return self._tag

    @property
    def attributes(self): return self._attributes

    def output(self):
        s = ""
        if self.document.output_break:
            if self.output_breakable and self.document.output_next_breakable:
                if self.level > 0:
                    s += "\n"
            s += self.document.output_retraction * self.level
        s += "<" + self.tag
        s += self.attributes.output()
        s += ">"
        self.document.output_next_breakable = True
        si = super().output()
        s += si
        if self.document.output_break:
            if si != "" and self.document.output_next_breakable:
                s += "\n" + "	" * self.level
        s += "</" + self.tag + ">"
        self.document.output_next_breakable = True
        return s
