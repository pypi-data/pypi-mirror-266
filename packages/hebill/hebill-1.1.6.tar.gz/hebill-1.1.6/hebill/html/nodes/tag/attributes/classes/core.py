class Classes(list):
    def reset(self, classes: str | list = None) -> bool:
        self.clear()
        if classes is None:
            return True
        return self.set(classes)

    def set(self, classes: str | list = None) -> bool:
        if classes is None:
            return False
        if isinstance(classes, str):
            self.extend(classes.split(' '))
            return True
        elif isinstance(classes, list):
            self.extend(classes)
            return True
        return False

    @property
    def is_empty(self) -> bool: return len(self) <= 0

    def __str__(self): return ' '.join(self)

    def output(self) -> str: return self.__str__()
