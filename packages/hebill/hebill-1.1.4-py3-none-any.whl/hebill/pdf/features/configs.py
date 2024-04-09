class Configs(dict):
    def __init__(self, document, senior=None, data=None):
        super().__init__()
        self._document = document
        self._senior = senior
        if data is not None:
            self.update(data)

    def __getitem__(self, key):
        if self.get(key) is not None:
            return self.get(key)
        if self._senior is not None:
            return self._senior[key]
        return None
