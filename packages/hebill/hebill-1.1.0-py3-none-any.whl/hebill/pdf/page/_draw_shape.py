from ._draw_line import _DrawLine


class _DrawShape(_DrawLine):
    def __init__(self, document, page, component):
        super().__init__(document, page, component)

    def draw(self):
        super().draw()
        self._page.xp('setFillColor', {'aColor': self.styles.fill_color, 'alpha': self.styles.fill_transparency})
        self._ps['stroke'] = 1 if self.styles.draw_line else 0
        self._ps['fill'] = 1 if self.styles.draw_fill else 0
