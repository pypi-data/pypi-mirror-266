from ....components.html.core import Html


class Libraries:
    def __init__(self, htm: Html):
        self._htm = htm
        self._files = []

    def add_js_file(self, url):
        if url not in self._files:
            self._files.append(url)
        pass

    def add_css_file(self, url):
        pass

    def use_hebill(self):
        pass
