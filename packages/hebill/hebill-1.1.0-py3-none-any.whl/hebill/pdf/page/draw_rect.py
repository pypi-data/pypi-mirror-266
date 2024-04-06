from ._draw_shape import _DrawShape


class DrawRect(_DrawShape):
    def __init__(self, document, page, component, x: float, y: float, w: float, h: float = None):
        super().__init__(document, page, component)
        self._ps['x'] = x * self.k
        self._ps['y'] = y * self.k
        self._ps['width'] = w * self.k if w > 0 else 10 * self.k
        self._ps['height'] = h * self.k if h is not None and h > 0 else self._ps['width']
        """
        rect(...)
         x: Any,
         y: Any,
         width: Any,
         height: Any,
         stroke: int = 1,
         fill: int = 0) -> None
         """

    def draw(self):
        super().draw()
        self._page.xp('rect', self._ps)
