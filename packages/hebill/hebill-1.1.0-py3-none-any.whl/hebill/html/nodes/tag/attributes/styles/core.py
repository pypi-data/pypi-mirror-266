class Styles(dict):
    def reset(self, styles: str | list = None) -> bool:
        self.clear()
        if styles is None:
            return True
        return self.set(styles)

    def set(self, styles: dict | str = None) -> bool:
        if isinstance(styles, str):
            if styles.strip() == '':
                return True
            if ';' not in styles:
                styles += ';'
            x = styles.split(';')
            for style in x:
                if ':' in style:
                    n, v = style.split(':')
                    self[n.strip()] = v.strip()
            return True
        elif isinstance(styles, dict):
            for n, v in styles.items():
                self[n] = v
            return True
        return False

    @property
    def is_empty(self) -> bool: return len(self) <= 0

    def __str__(self): return ''.join(f'{n}:{v};' for n, v in self.items())

    def output(self) -> str: return self.__str__()
