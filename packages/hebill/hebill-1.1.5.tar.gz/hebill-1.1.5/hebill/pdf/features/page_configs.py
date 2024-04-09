from .configs import Configs


class PageConfigs(Configs):
    def __init__(self, document, senior=None, data=None):
        super(PageConfigs, self).__init__(document, senior, data)

    @property
    def width(self): return self['width']

    @width.setter
    def width(self, width):
        if width > 0:
            self['width'] = width

    @property
    def height(self): return self['height']

    @height.setter
    def height(self, height: float):
        if height > 0:
            self['height'] = height

    @property
    def margin_top(self): return self['margin_top']

    @margin_top.setter
    def margin_top(self, margin: float):
        if margin > 0:
            self['margin_top'] = margin

    @property
    def margin_right(self): return self['margin_right']

    @margin_right.setter
    def margin_right(self, margin: float):
        if margin > 0:
            self['margin_right'] = margin

    @property
    def margin_bottom(self): return self['margin_bottom']

    @margin_bottom.setter
    def margin_bottom(self, margin: float):
        if margin > 0:
            self['margin_bottom'] = margin

    @property
    def margin_left(self): return self['margin_left']

    @margin_left.setter
    def margin_left(self, margin: float):
        if margin > 0:
            self['margin_left'] = margin
