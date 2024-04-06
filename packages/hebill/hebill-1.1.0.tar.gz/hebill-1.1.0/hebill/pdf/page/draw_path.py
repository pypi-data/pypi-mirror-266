import math
from ._draw_shape import _DrawShape


class DrawPath(_DrawShape):
    def __init__(self, document, page, component):
        super().__init__(document, page, component)
        self._paths = []
        self._moved_to = False
        self._closed = False

    def move_to(self, x, y):
        self._paths.append(['move_to', {'x': x * self.k, 'y': y * self.k}])
        self._moved_to = True

    def line_to(self, x, y):
        if not self._moved_to:
            self.move_to(x, y)
            return
        self._paths.append(['line_to', {'x': x * self.k, 'y': y * self.k}])

    def arc_to(self, x: float, y: float, r: float, start_angle: float = 0, end_angle: float = 90):
        # 每两度一条直线
        n = int(abs((end_angle - start_angle) / 2))
        if n < 3:
            n = 3
        step = (end_angle - start_angle) / n
        for i in range(0, n + 1):
            angle = start_angle + i * step
            radian = angle * math.pi / 180
            point_x = x + r * math.cos(radian)
            point_y = y + r * math.sin(radian)
            # 将点添加到路径中
            self.line_to(point_x, point_y)

    def close(self):
        self._paths.append(['close', []])

    def draw(self, close: bool = False):
        if len(self._paths) <= 0:
            return
        if self.styles.draw_fill or (close and not self._closed):
            self.close()
        super().draw()
        self._page.xp('beginPath', [self._paths, self._ps])
