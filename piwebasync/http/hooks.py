from typing import Union
import httpx

from .safeurl import SafeURL


async def use_safe_url_hook(safe: str, obj: Union[httpx.Request, httpx.Response]):
    """Request/Response hook for modifying percent encoding of urls"""
    safe_url = SafeURL(safe, obj.url)
    if isinstance(obj, httpx.Request):
        obj.url = safe_url
    else:
        obj.request.url = safe_url