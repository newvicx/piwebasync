from typing import Union
import httpx

from .models import SafeURL


async def use_safe_url_hook(safe: str, obj: Union[httpx.Request, httpx.Response]):
    """Request/Response hook for modifying percent encoding of urls"""
    safe_url = SafeURL(safe, obj.url)
    obj.url = safe_url