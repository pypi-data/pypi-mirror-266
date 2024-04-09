from ._draw_ import Draw


class _DrawLine(Draw):
    def __init__(self, document, page, component):
        super().__init__(document, page, component)

    def draw(self):
        self._page.xp('setLineWidth', {'width': self.styles.line_width * self.k})
        self._page.xp('setStrokeColor', {'aColor': self.styles.line_color, 'alpha': self.styles.line_transparency})
