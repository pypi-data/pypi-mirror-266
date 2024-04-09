class Nodes:
    def __init__(self, sir):
        self.senior = sir

    def code(self, text: str = None):
        from .....nodes import Code
        return Code(self.senior, text)

    def content(self, text: str = None):
        from .....nodes import Content
        return Content(self.senior, text)

    def comment(self, text: str = None):
        from .....nodes import Comment
        return Comment(self.senior, text)

    def group(self):
        from .....nodes import Group
        return Group(self.senior)

    def tag(self, name: str):
        from .....nodes import Tag
        return Tag(self.senior, name)
