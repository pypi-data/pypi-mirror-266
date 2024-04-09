from ...nodes.node.core import Node


class Code(Node):
    def __init__(self, sir, text: str = ''):
        super().__init__(sir)
        self.text = text

    def output(self):
        self.document.output_end_breakable = False
        return f"{self.text}"
