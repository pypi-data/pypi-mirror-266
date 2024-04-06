from ..node.core import Node


class Content(Node):
    def __init__(self, sir, text: str = None):
        super().__init__(sir)
        self.text = text if text is not None else ''

    def output(self):
        self.document.output_next_breakable = False
        return self.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
