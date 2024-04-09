from ..node.core import Node


class Comment(Node):
    def __init__(self, sir, text: str = None):
        super().__init__(sir)
        self.text = text if text is not None else ''

    def output(self):
        s = ""
        if self.document.output_break:
            s += "\n" + self.document.output_retraction * self.level
        s += f"<!--[{self.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}]-->"
        self.document.output_next_breakable = True
        return s
