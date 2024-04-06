from . _draw_line import _DrawLine


class DrawLine(_DrawLine):
    def __init__(self, document, page, component, x1: float, y1: float, x2: float, y2: float):
        super().__init__(document, page, component)
        self._ps['x1'] = x1 * self.k
        self._ps['y1'] = y1 * self.k
        self._ps['x2'] = x2 * self.k
        self._ps['y2'] = y2 * self.k

    def draw(self):
        super().draw()
        self._page.xp('line', self._ps)
