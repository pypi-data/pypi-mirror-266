from ._draw_text import _DrawText


class DrawString(_DrawText):
    def __init__(self, document, page, component, x: float, y: float, text: str):
        super().__init__(document, page, component)
        self._ps['x'] = x * self.k
        self._ps['y'] = y * self.k
        self._ps['text'] = text

    def draw(self):
        super().draw()
        if self.styles.text_character_space is not None:
            self._ps['charSpace'] = self.styles.text_character_space * self.k
        if self.styles.text_word_space is not None:
            self._ps['wordSpace'] = self.styles.text_word_space * self.k
        self._page.xp('drawString', self._ps)
