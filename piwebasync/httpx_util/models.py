import urllib.parse

import httpx

class SafeURL(httpx.URL):

    """
    Wrapper around HTTPX URL for specifying characters that should and
    should not be % encoded in the URL target
    """

    def __init__(self, safe: str, url: httpx.URL) -> None:
        self._safe = safe
        super().__init__(url)

    @property
    def raw_path(self) -> bytes:
        """Unquote encoded URL and requote with safe chars"""
        raw = super().raw_path
        safe = urllib.parse.quote(
            urllib.parse.unquote(raw.decode("ascii"), encoding="ascii"),
            safe=self._safe
        )
        return safe.encode("ascii")