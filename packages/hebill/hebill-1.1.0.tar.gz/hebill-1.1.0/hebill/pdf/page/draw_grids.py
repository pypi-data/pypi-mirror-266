from . _draw_line import _DrawLine


class DrawGrids(_DrawLine):
    def __init__(self, document, page, component, w: float = None, h: float = None):
        super().__init__(document, page, component)
        self._w = w
        self._h = h

    def draw(self):
        super().draw()
        if self._w is None or self._w <= 0:
            self._w = self.styles.grid_width
            self._h = self.styles.grid_height
        if self._h is None or self._h <= 0:
            self._h = self._w
        width_quantity = int(self.page.configs.width / self._w)
        height_quantity = int(self.page.configs.height / self._h)
        super().draw()
        k = self.k
        for i in range(1, width_quantity + 1):
            x = i * self._w * k
            self.page.xp('line', {'x1': x, 'y1': 0, 'x2': x, 'y2': self.page.configs.height * k})
        for i in range(1, height_quantity + 1):
            y = i * self._h * k
            self.page.xp('line', {'x1': 0, 'y1': y, 'x2': self.page.configs.width * k, 'y2': y})
