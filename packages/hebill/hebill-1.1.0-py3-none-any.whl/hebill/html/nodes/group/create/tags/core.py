class Tags:
    def __init__(self, sir):
        self.senior = sir

    def a(self, title: str = None, url: str = None):
        from .....tags import A
        return A(self.senior, title, url)

    def body(self):
        from .....tags import Body
        return Body(self.senior)

    def div(self, text: str = None):
        from .....tags import Div
        return Div(self.senior, text)

    def h1(self, text: str = None):
        from .....tags import H1
        return H1(self.senior, text)

    def h2(self, text: str = None):
        from .....tags import H2
        return H2(self.senior, text)

    def h3(self, text: str = None):
        from .....tags import H3
        return H3(self.senior, text)

    def h4(self, text: str = None):
        from .....tags import H4
        return H4(self.senior, text)

    def h5(self, text: str = None):
        from .....tags import H5
        return H5(self.senior, text)

    def h6(self, text: str = None):
        from .....tags import H6
        return H6(self.senior, text)

    def head(self):
        from .....tags import Head
        return Head(self.senior)

    def html(self, lang: str = None):
        from .....tags import Html
        return Html(self.senior, lang)

    def input_text(self, name: str = None, value: str | int | float = None, placeholder: str = None):
        from .....tags import InputText
        return InputText(self.senior, name, value, placeholder)

    def link(self, url: str = None):
        from .....tags import Link
        return Link(self.senior, url)

    def script(self, url: str = None):
        from .....tags import Script
        return Script(self.senior, url)

    def span(self, text: str = None):
        from .....tags import Span
        return Span(self.senior, text)

    def table(self):
        from .....tags import Table
        return Table(self.senior)

    def tbody(self):
        from .....tags import Tbody
        return Tbody(self.senior)

    def th(self):
        from .....tags import Th
        return Th(self.senior)

    def td(self):
        from .....tags import Td
        return Td(self.senior)

    def thead(self):
        from .....tags import Thead
        return Thead(self.senior)

    def title(self, text: str = None):
        from .....tags import Title
        return Title(self.senior, text)

    def tr(self):
        from .....tags import Tr
        return Tr(self.senior)
