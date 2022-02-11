import urllib.parse
from typing import Optional

import httpx

class SafeURL:

    """
    Wrapper around HTTPX URL for specifying characters that should and
    should not be % encoded in the URL target
    """

    def __init__(self, url: httpx.URL, safe: str) -> None:
        self._url = url
        self._safe = safe

    @property
    def scheme(self) -> str:
        return self._url.scheme

    @property
    def raw_scheme(self) -> bytes:
        return self._url.raw_scheme

    @property
    def userinfo(self) -> bytes:
        return self._url.userinfo

    @property
    def username(self) -> str:
        return self._url.username

    @property
    def password(self) -> str:
        return self._url.password

    @property
    def host(self) -> str:
        return self._url.host

    @property
    def raw_host(self) -> bytes:
        return self._url.raw_host

    @property
    def port(self) -> Optional[int]:
        return self._url.port

    @property
    def netloc(self) -> bytes:
        return self._url.netloc

    @property
    def path(self) -> str:
        return self._url.path

    @property
    def query(self) -> bytes:
        return self._url.query

    @property
    def params(self) -> "QueryParams":
        return self._url.params

    @property
    def raw_path(self) -> bytes:
        raw = self._url.raw_path
        safe = urllib.parse.quote(
            urllib.parse.unquote(raw.decode("ascii"), encoding="ascii"),
            safe=self._safe
        )
        return safe.encode("ascii")

    @property
    def fragment(self) -> str:
        return self._url.fragment

    @property
    def raw(self) -> httpx._models.RawURL:
        return self._url.raw