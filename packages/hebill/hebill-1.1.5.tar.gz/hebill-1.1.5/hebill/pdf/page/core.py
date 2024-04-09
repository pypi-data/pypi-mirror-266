from .draw_rect import DrawRect
from .draw_grids import DrawGrids
from .draw_ellipse import DrawEllipse
from .draw_circle import DrawCircle
from .draw_line import DrawLine
from .draw_string import DrawString
from .draw_path import DrawPath
from ..features.page_configs import PageConfigs
from ..features.styles import Styles


class Page:
    def __init__(self, document, number, size=None):
        from ..core import Document
        self._document: Document = document
        self._number = number
        self.size = size
        self._xs = []
        self._configs = PageConfigs(self.document, self.document.page_configs)
        self._styles = Styles(self.document, self.document.styles)
        # 单位和页面尺寸处理
        if isinstance(size, list) or isinstance(size, tuple):
            (self.configs.width, self.configs.height) = size
        elif number > 1:
            self.configs.width = self._document.configs.width
            self.configs.height = self._document.configs.height
        else:
            self.configs.width = 210 / 25.4 * 72 / self._document.unit_ratio
            self.configs.height = 297 / 25.4 * 72 / self._document.unit_ratio
        if number == 1:
            self._document.configs.width = self.configs.width
            self._document.configs.height = self.configs.height
        if number > 1:
            self.xp('showPage')
        self.xp('setPageSize', {'size': (self.configs.width * self._document.unit_ratio,
                                self.configs.height * self._document.unit_ratio)})

    @property
    def xs(self): return self._xs

    def xp(self, m, a=None):
        self._xs.append([m, a])

    @property
    def configs(self) -> PageConfigs: return self._configs

    @property
    def styles(self) -> Styles: return self._styles

    @property
    def document(self): return self._document

    @property
    def k(self): return self.document.k

    @property
    def number(self): return self._number

    def draw_string(self, x: float, y: float, text: str) -> DrawString:
        return DrawString(self.document, self, None, x, y, text)

    def draw_line(self, x1: float, y1: float, x2: float, y2: float) -> DrawLine:
        return DrawLine(self.document, self, None, x1, y1, x2, y2)

    def draw_circle(self, x: float, y: float, r: float) -> DrawCircle:
        return DrawCircle(self.document, self, None, x, y, r)

    def draw_ellipse(self, x1: float, y1: float, x2: float, y2: float) -> DrawEllipse:
        return DrawEllipse(self.document, self, None, x1, y1, x2, y2)

    def draw_path(self) -> DrawPath:
        return DrawPath(self.document, self, None)

    def draw_grids(self, w: float = None, h: float = None) -> DrawGrids:
        return DrawGrids(self.document, self, None, w, h)

    def draw_rect(self, x: float, y: float, w: float, h: float = None) -> DrawRect:
        return DrawRect(self.document, self, None, x, y, w, h)
