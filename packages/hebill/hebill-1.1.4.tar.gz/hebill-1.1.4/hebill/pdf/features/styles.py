from .configs import Configs
from ..library.configs_selector_color import ColorSelector
from ..library.configs_selector_font import FontSelector


class Styles(Configs):
    def __init__(self, document, senior=None, data=None):
        super(Styles, self).__init__(document, senior, data)
        self._text_color_selector = None
        self._font_selector = None
        self._line_color_selector = None
        self._fill_color_selector = None

    ####################################################################################################
    # Text Configs
    ####################################################################################################
    @property
    def text_color(self): return self['text_color']

    @property
    def text_color_selector(self):
        if self._text_color_selector is None:
            self._text_color_selector = ColorSelector(self, 'text_color')
        return self._text_color_selector

    @property
    def text_transparency(self): return self['text_transparency']

    @text_transparency.setter
    def text_transparency(self, transparency):
        if 0 <= transparency <= 1:
            self['text_transparency'] = transparency

    @property
    def text_height(self): return self['text_height']

    @text_height.setter
    def text_height(self, height: float):
        if height > 0:
            self['text_height'] = height

    @property
    def font_name(self): return self['font_name']

    @property
    def font_selector(self):
        if self._font_selector is None:
            self._font_selector = FontSelector(self._document, self, 'font_name')
        return self._font_selector

    @property
    def text_character_space(self): return self['text_character_space']

    @text_character_space.setter
    def text_character_space(self, space: float): self['text_character_space'] = space

    @property
    def text_word_space(self): return self['text_word_space']

    @text_word_space.setter
    def text_word_space(self, space: float): self['text_word_space'] = space

    @property
    def text_direction(self): return self['text_direction']

    # TODO

    ####################################################################################################
    # Line Configs
    ####################################################################################################

    @property
    def draw_line(self): return self['draw_line']

    @draw_line.setter
    def draw_line(self, draw: bool = True): self['draw_line'] = draw

    @property
    def line_width(self): return self['line_width']

    @line_width.setter
    def line_width(self, width: float):
        self['line_width'] = width

    @property
    def line_color(self): return self['line_color']

    @property
    def line_color_selector(self):
        if self._line_color_selector is None:
            self._line_color_selector = ColorSelector(self, 'line_color')
        return self._line_color_selector

    @property
    def line_transparency(self): return self['line_transparency']

    @line_transparency.setter
    def line_transparency(self, transparency):
        if 0 <= transparency <= 1:
            self['line_transparency'] = transparency

    ####################################################################################################
    # Fill Configs
    ####################################################################################################

    @property
    def draw_fill(self): return self['draw_fill']

    @draw_fill.setter
    def draw_fill(self, draw: bool = True): self['draw_fill'] = draw

    @property
    def fill_color(self): return self['fill_color']

    @property
    def fill_color_selector(self):
        if self._fill_color_selector is None:
            self._fill_color_selector = ColorSelector(self, 'fill_color')
        return self._fill_color_selector

    @property
    def fill_transparency(self): return self['fill_transparency']

    @fill_transparency.setter
    def fill_transparency(self, transparency):
        if 0 <= transparency <= 1:
            self['fill_transparency'] = transparency

    ####################################################################################################
    # Grids Configs
    ####################################################################################################

    @property
    def grid_width(self): return self['grid_width']

    @grid_width.setter
    def grid_width(self, width):
        if width > 0:
            self['grid_width'] = width

    @property
    def grid_height(self): return self['grid_height']

    @grid_height.setter
    def grid_height(self, height):
        if height > 0:
            self['grid_height'] = height
