import httpx

from .models import SafeURL


async def use_safe_url_hook(safe: str, request: httpx.Request):
    safe_url = SafeURL(request.url, safe)
    request.url = safe_url