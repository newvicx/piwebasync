import functools
import urllib.parse
from types import TracebackType
from typing import(
    Any,
    Callable,
    List,
    Mapping,
    Type,
    Union
)

from httpx import (
    AsyncBaseTransport,
    Auth,
    Headers,
    Limits,
    Request,
    Response,
    URL
)
from httpx._client import UseClientDefault, USE_CLIENT_DEFAULT
from httpx._config import (
    DEFAULT_TIMEOUT_CONFIG,
    DEFAULT_MAX_REDIRECTS
)
from httpx._types import(
    AuthTypes,
    CertTypes,
    CookieTypes,
    HeaderTypes,
    ProxiesTypes,
    TimeoutTypes
)
from httpx_extensions import ExClient

from piwebasync.api import APIRequest, APIResponse
from piwebasync.exceptions import HTTPClientError



async def safe_url_hook(safe: str, obj: Union[Request, Response]):
    """Request/Response hook for modifying percent encoding of urls"""
    safe_url = SafeURL(safe, obj.url)
    if isinstance(obj, Request):
        obj.url = safe_url
    else:
        obj.request.url = safe_url


class SafeURL(URL):

    """
    Wrapper around HTTPX URL for specifying characters that should and
    should not be % encoded in the URL target
    """

    def __init__(self, url: URL, safe: str = None) -> None:
        default_safe = ":/?#[]@!$&'()*+,;="
        safe = safe or ''
        default_safe += safe
        self._safe = default_safe
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


class HTTPClient:

    """
    Asynchronous HTTP client for making requests to a Pi Web API server

    **Usage**

    ```python
    request = Controller(scheme, host, root=root).streams.get_end(webid)
    async with piwebasync.HTTPClient() as client:
        response = await client.get(request)
    ```

    **Parameters**

    - **auth** (*Optional*): An authentication class to use when sending
    requests.
    - **headers** (*Optional*): Dictionary of HTTP headers to include
    when sending requests.
    - **cookies** (*Optional*): Dictionary of Cookie items to include
    when sending requests.
    - **verify** (*Optional*): SSL certificates (a.k.a CA bundle) used
    to verify the identity of requested hosts. Either True (default CA bundle),
    a path to an SSL certificate file, an ssl.SSLContext, or False (which will
    disable verification).
    - **safe_chars** (*Optional*): String of safe characters that should
    not be percent encoded
    - **cert** (*Optional*): An SSL certificate used by the requested host
    to authenticate the client. Either a path to an SSL certificate file, or
    two-tuple of (certificate file, key file), or a three-tuple of (certificate
    file, key file, password).
    - **proxies** (*Optional*): A dictionary mapping proxy keys to proxy URLs.
    - **mounts** (*Optional*): A dictionary of mounted transports against a given
    schema or domain
    - **timeout** (*Optional*): The timeout configuration to use when sending requests.
    - **follow_redirects** (*Optional*): Boolean flag indicating if client should
    follow redirects
    - **max_connections** (*Optional*): The maximum concurrent connections to open
    - **max_redirects** (*Optional*): The maximum number of redirect responses
    that should be followed.
    - **event_hooks** (*Optional*): Dictionary of async callables with signature
    *Callable[[Union[httpx.Request, httpx.Response]], Union[httpx.Request, httpx.Response]]*
    - **transport** (*Optional*): A transport class to use for sending requests over
    the network.
    - **trust_env** (*Optional*) Enables or disables usage of environment variables
    for configuration.

    The underlying client (ExClient) API mimics the HTTPX API and supports many of its features...
    https://www.python-httpx.org/async/

    For key differences between the httpx_extensions.ExClient and httpx.AsyncClient
    see this README...
    https://github.com/newvicx/httpx_extensions/blob/main/README.md

    For more infomation on the PI Web API and the different controllers
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help.html

    For Pi Web API Channels, use the WebsocketClient class
    """

    def __init__(
        self,
        auth: Auth = None,
        headers: Headers = None,
        cookies: CookieTypes = None,
        verify: bool = True,
        safe_chars: str = None,
        cert: CertTypes = None,
        proxies: ProxiesTypes = None,
        mounts: Mapping[str, AsyncBaseTransport] = None,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
        follow_redirects: bool = False,
        max_connections: int = 50,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        event_hooks: Mapping[str, List[Callable]] = None,
        transport: AsyncBaseTransport = None,
        trust_env: bool = True,
    ) -> None:

        limits = Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_connections
        )
        event_hooks = self._configure_hooks(
            safe_chars=safe_chars,
            event_hooks=event_hooks
        )    
        self.client = ExClient(
            auth=auth,
            headers=headers,
            cookies=cookies,
            verify=verify,
            cert=cert,
            proxies=proxies,
            mounts=mounts,
            timeout=timeout,
            follow_redirects=follow_redirects,
            limits=limits,
            max_redirects=max_redirects,
            event_hooks=event_hooks,
            transport=transport,
            trust_env=trust_env
        )

    async def request(
        self,
        request: APIRequest,
        *,
        headers: HeaderTypes = None,
        json: Any = None,
        auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: dict = None,
    ) -> APIResponse:
        """
        Verify and send APIRequest

        **Parameters**
        - **request** (*APIRequest*): request to send
        - **headers** (*Optional*): Dictionary of HTTP headers to include for this request
        - **json** (*Optional*): Dictionary of JSON encoded data to send in request body
        - **auth** (*Optional*): An authentication class to use for this request
        - **follow_redirects** (*Optional*): Boolean flag indicating client should follow
        redirects for this request
        - **timeout** (*Optional*): The timeout configuration to use for this request
        - **extensions** (*Optional*): Dictionary of request extensions to use for this
        request

        **Returns**
        - **APIResponse**: response object containing response info and content

        **Raises**
        - **HTTPClientError**: error sending request. Always originates from an error in
        the underlying client object. Will always have a `__cause__` attribute
        - **ValueError**: invalid APIRequest protocol for client (i.e. not HTTP)
        - **TypeError**: request is not an instance of APIRequest
        """

        if not isinstance(request, APIRequest):
            raise TypeError(
                f"'request' must be instance of APIRequest. Got {type(request)}"
            )
        if request.protocol != "HTTP":
            raise ValueError(
                f"Invalid protocol for {self.__class__.__name__}. Expected 'HTTP', "
                f"got '{request.protocol}'. If this is a websocket request, use the "
                "WebsocketClient"
            )
        request_to_send = self.client.build_request(
            method=request.method,
            url=request.absolute_url,
            json=json,
            headers=headers,
            timeout=timeout,
            extensions=extensions
        )
        try:
            response = await self.client.send(
                request_to_send,
                auth=auth,
                follow_redirects=follow_redirects
            )
        except BaseException as err:
            raise HTTPClientError(
                "An error occurred handling the HTTP request"
            ) from err
        return request.response_model(response=response)

    async def get(
        self,
        request: APIRequest,
        *,
        headers: HeaderTypes = None,
        auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: dict = None,
    ) -> APIResponse:
        """
        Verify and send a GET APIRequest

        **Parameters**
        - See ***HTTPClient.request*** (Does not accept *json* parameter)

        **Returns**
        - See ***HTTPClient.request***

        **Raises**
        - See ***HTTPClient.request***
        """
        return await self.request(
            request,
            headers=headers,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions
        )
    
    async def post(
        self,
        request: APIRequest,
        *,
        headers: HeaderTypes = None,
        json: Any = None,
        auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: dict = None
    ) -> APIResponse:
        """
        Verify and send a POST APIRequest

        **Parameters**
        - See ***HTTPClient.request***

        **Returns**
        - See ***HTTPClient.request***

        **Raises**
        - See ***HTTPClient.request***
        """
        return await self.request(
            request,
            headers=headers,
            json=json,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions
        )

    async def put(
        self,
        request: APIRequest,
        *,
        headers: HeaderTypes = None,
        json: Any = None,
        auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: dict = None
    ) -> APIResponse:
        """
        Verify and send a PUT APIRequest

        **Parameters**
        - See ***HTTPClient.request***

        **Returns**
        - See ***HTTPClient.request***

        **Raises**
        - See ***HTTPClient.request***
        """
        return await self.request(
            request,
            headers=headers,
            json=json,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions
        )

    async def patch(
        self,
        request: APIRequest,
        *,
        headers: HeaderTypes = None,
        json: Any = None,
        auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: dict = None
    ) -> APIResponse:
        """
        Verify and send a PATCH APIRequest

        **Parameters**
        - See ***HTTPClient.request***

        **Returns**
        - See ***HTTPClient.request***

        **Raises**
        - See ***HTTPClient.request***
        """
        return await self.request(
            request,
            headers=headers,
            json=json,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions
        )

    async def delete(
        self,
        request: APIRequest,
        *,
        headers: HeaderTypes = None,
        auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: dict = None
    ) -> APIResponse:
        """
        Verify and send a DELETE APIRequest

        **Parameters**
        - See ***HTTPClient.request***

        **Returns**
        - See ***HTTPClient.request***

        **Raises**
        - See ***HTTPClient.request***
        """
        return await self.request(
            request,
            headers=headers,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions
        )
    
    async def aclose(self) -> None:
        """
        Close the HTTPClient
        """
        await self.client.aclose()

    def _configure_hooks(
        self,
        safe_chars: str = None,
        event_hooks: Mapping[str, List[Callable]] = None,
    ) -> Mapping[str, List[Callable]]:
        """
        Configure event hooks to support safe chars if specified
        
        Raises:
            - TypeError: safe_chars are not strings
        """
        event_hooks = event_hooks or {}
        safe_chars = safe_chars or ''
        if not isinstance(safe_chars, str):
            raise TypeError(
                f"Invalid type for 'safe_chars'. Expected 'str', got {type(safe_chars)}"
            )
        hook = functools.partial(safe_url_hook, safe_chars)
        request_hooks = list(event_hooks.get("request", []))
        response_hooks = list(event_hooks.get("response", []))
        request_hooks.insert(0, hook)
        response_hooks.insert(0, hook)
        event_hooks.update(
            {
                "request": request_hooks,
                "response": response_hooks
            }
        )
        return event_hooks

    async def __aenter__(self) -> "HTTPClient":
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] = None,
        exc_value: BaseException = None,
        traceback: TracebackType = None,
    ) -> None:
        await self.aclose()