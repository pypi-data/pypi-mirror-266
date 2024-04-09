from .classes.core import Classes
from .styles.core import Styles


class Attributes(dict):
    def __init__(self):
        super().__init__()
        self._classes: Classes = Classes(self)
        self._styles: Styles = Styles(self)

    def __setitem__(self, key: str, value):
        key = key.lower()
        if key == 'class':
            self.classes.set(value)
            print('验证classes' + value)
            super().__setitem__(key, '')
        elif key == 'style':
            self.styles.set(value)
            print('验证styles' + value)
            super().__setitem__(key, '')
        else:
            super().__setitem__(key, value)
        
    def __getitem__(self, key):
        key = key.lower()
        if key == 'class':
            return self.classes.output()
        elif key == 'style':
            return self.styles.output()
        else:
            return super().__getitem__(key)

    def is_empty(self) -> bool: return self.classes.is_empty and self.styles.is_empty and len(self) <= 0

    @property
    def classes(self): return self._classes

    @property
    def styles(self): return self._styles

    def __str__(self):
        if len(self.classes) > 0:
            super().__setitem__('class', self.classes.output())
        if len(self.styles) > 0:
            super().__setitem__('style', self.styles.output())
        return ''.join(f" {n}=\"{v}\"" for n, v in self.items())

    def output(self) -> str: return self.__str__()
