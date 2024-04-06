from ._draw_ import Draw


class _DrawText(Draw):
    def __init__(self, document, page, component):
        super().__init__(document, page, component)

    def draw(self):
        self._page.xp('setFont', {'psfontname': self.styles.font_name,
                                  'size': self.styles.text_height * self.k})
        self._page.xp('setFillColor', {'aColor': self.styles.text_color, 'alpha': self.styles.line_transparency})
