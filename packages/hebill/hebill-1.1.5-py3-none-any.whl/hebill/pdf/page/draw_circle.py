from ._draw_shape import _DrawShape


class DrawCircle(_DrawShape):
    def __init__(self, document, page, component, x: float, y: float, r: float):
        super().__init__(document, page, component)
        self._ps['x_cen'] = x * self.k
        self._ps['y_cen'] = y * self.k
        self._ps['r'] = r * self.k

    def draw(self):
        super().draw()
        self._page.xp('circle', self._ps)
