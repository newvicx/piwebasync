import urllib.parse

from httpx import URL

class SafeURL(URL):

    """
    Wrapper around HTTPX URL for specifying characters that should and
    should not be % encoded in the URL target
    """

    def __init__(self, safe: str, url: URL) -> None:
        self._safe = safe
        super().__init__(url)

    @property
    def raw_path(self) -> bytes:
        """Unquote encoded URL and requote with safe chars"""
        raw: bytes = super().raw_path
        safe: str = urllib.parse.quote(
            urllib.parse.unquote(raw.decode("ascii"), encoding="ascii"),
            safe=self._safe
        )
        return safe.encode("ascii")

    def __str__(self) -> str:
        """Unquote encoded URL and requote with safe chars"""
        raw: str = super().__str__()
        return urllib.parse.quote(
            urllib.parse.unquote(raw, encoding="ascii"),
            safe=self._safe
        )
