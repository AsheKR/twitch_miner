class CookieNameNotFoundException(Exception):
    def __init__(self, name: str):
        self._name = name
