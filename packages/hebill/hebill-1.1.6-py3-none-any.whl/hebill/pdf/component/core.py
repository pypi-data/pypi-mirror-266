from ..page.draw_rect import DrawRect
from ..page.draw_grids import DrawGrids
from ..page.draw_ellipse import DrawEllipse
from ..page.draw_circle import DrawCircle
from ..page.draw_line import DrawLine
from ..page.draw_string import DrawString
from ..page.draw_path import DrawPath
from ..features.styles import Styles


class Component:
    def __init__(self, document, page, component, x: float = 0, y: float = 0, k: float = 1):
        from ..core import Document
        self._document: Document = document
        self._component: Component = component
        self._page = page if page is not None else self.document.page
        self._xs: float = x
        self._ys: float = y
        self._xe: float = x
        self._ye: float = y
        self._k: float = k
        if self.component is None:
            self._styles = Styles(self.document, self.page.styles)
        else:
            self._styles = Styles(self.document, self.component.styles)

    @property
    def document(self): return self._document

    @property
    def page(self): return self._page

    @property
    def component(self): return self._component

    @property
    def k(self): return self._k

    @property
    def xs(self): return self._xs

    @property
    def ys(self): return self._ys

    @property
    def xe(self): return self._xe
    
    @property
    def ye(self): return self._ye

    @property
    def styles(self) -> Styles: return self._styles

    def draw_string(self, x: float, y: float, text: str) -> DrawString:
        return DrawString(self.document, self.page, self, x, y, text)

    def draw_line(self, x1: float, y1: float, x2: float, y2: float) -> DrawLine:
        return DrawLine(self.document, self.page, self, x1, y1, x2, y2)

    def draw_circle(self, x: float, y: float, r: float) -> DrawCircle:
        return DrawCircle(self.document, self.page, self, x, y, r)

    def draw_ellipse(self, x1: float, y1: float, x2: float, y2: float) -> DrawEllipse:
        return DrawEllipse(self.document, self.page, self, x1, y1, x2, y2)

    def draw_path(self) -> DrawPath:
        return DrawPath(self.document, self.page, self)

    def draw_grids(self, w: float = None, h: float = None) -> DrawGrids:
        return DrawGrids(self.document, self.page, self, w, h)

    def draw_rect(self, x: float, y: float, w: float, h: float = None):
        return DrawRect(self.document, self, self, x, y, w, h)
