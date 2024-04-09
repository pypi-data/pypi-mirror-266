from ..features.styles import Styles


class Draw:
    def __init__(self, document, page, component):
        from ..core import Document
        self._document: Document = document
        from .core import Page
        self._page: Page = page
        from ..component.core import Component
        self._component: Component | None = component
        if self.component is None:
            self._styles = Styles(self.document, self.page.styles)
        else:
            self._styles = Styles(self.document, self.component.styles)
        self._ps = {}

    @property
    def document(self): return self._document

    @property
    def page(self): return self._page

    @property
    def component(self): return self._component

    @property
    def k(self): return self.document.k

    @property
    def styles(self) -> Styles: return self._styles
