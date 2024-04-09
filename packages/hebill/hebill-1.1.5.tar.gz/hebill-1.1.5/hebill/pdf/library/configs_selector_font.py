class FontSelector:
    def __init__(self, document, configs, dict_key):
        from ..core import Document
        self._document: Document = document
        self._configs = configs
        self._dict_key = dict_key

    def _set(self, i):
        self._document.add_font(i)
        self._configs[self._dict_key] = i

    def wen_quan_yi_hei(self):
        self._set('WenQuanYiMicroHei')

    def wen_quan_yi_hei_regular(self):
        self._set('WenQuanYiMicroHeiRegular')

    def microsoft_ya_hei(self):
        self._set('MicrosoftYaHei')

    def microsoft_ya_hei_bold(self):
        self._set('MicrosoftYaHeiBold')

    def vinet(self):
        self._set('Vinet')

    def arial_narrow(self):
        self._set('ArialNarrow')

    def awesome_web(self):
        self._set('AwesomeWeb')
