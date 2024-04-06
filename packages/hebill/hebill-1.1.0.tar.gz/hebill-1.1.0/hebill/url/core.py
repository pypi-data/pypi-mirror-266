class Url:
    def __init__(self, url: str):
        self._url = url

    @property
    def url(self) -> str: return self._url

    def fetch(self) -> str:
        import requests
        fetch = requests.get(self.url)
        if fetch.status_code == 200:
            return fetch.text
        return ''
