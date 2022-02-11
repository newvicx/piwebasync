import functools
from types import TracebackType
from typing import(
    Callable,
    List,
    Mapping,
    Type,
    Union
)

import orjson
from httpx import (
    AsyncBaseTransport,
    AsyncClient,
    Auth,
    Headers,
    Limits
)
from httpx._client import UseClientDefault, USE_CLIENT_DEFAULT
from httpx._config import (
    DEFAULT_LIMITS,
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

from .api.models import APIRequest, APIResponse
from .api.controllers.base import BaseController
from .exceptions import HTTPClientError
from .httpx_util.hooks import use_safe_url_hook



class HTTPClient:

    """
    An asynchronous HTTP client for making requests to a Pi Web API server.
    This client is built off HTTPX and mimics the API closely. Kerberos and
    NTLM authentication are supported. If using GSSAPI you can use the stock
    AsyncClient with httpx_gssapi auth handler. If using SSPI, you will need
    to use the ExClient from httpx_extensions which has an identical API HTTPX
    but adds additional support for connection management.

    Usage:
    >>> async with piwebasync.HTTPClient as client:
    >>>     response = await client.get(Streams.get_recorded(webid))

    Parameters
    - scheme (Optional[str]): the url scheme to use, either http or https
    - host (Optional[str]): the host to connect to
    - port (Optional[str]): the port to connect to
    - root (Optional[str]): the root path to the Pi Web API ``https://myhost/root``
    defaults to '/'
    - safe_chars (Optional[str]): an optional string containing characters which
    should not be percent encoded when sending the request. urllib.parse.quote is
    used to achieve this. Note that httpx's event hook system is used to wrap the
    default URL class before the request is sent and after the response is received.
    It will always be the first hook executed in both cases.
    - client (Optional[Union[ExClient, AsyncClient]]): client used to fulfill requests,
    the default is ExClient. Note that the ExClient only works for HTTP 1.1 requests.
    - normalize_response_content (Optional[bool]): if true converts top level keys in
    response content from camel case to snake case (WebId -> web_id). This can be useful
    in certain situations where you want to access attributes straigt from the response
    in a pythonic way. For example if normalize_response_content = True, I can access the
    WebId from a response (if it is in the top level of the body) as an attribute
    ``web_id = response.web_id``. If normalize_response_content = False you can
    still access the attribute using camel case ``web_id = response.WebId``

    The rest of parameters are directly from httpx.AsyncClient. Note that when using
    the ExClient though, the 'http1', 'http2', and 'app' parameters are ignored entirely.
    They are there for compatability with httpx.AsyncClient

    Visit the Pi Web API reference to get familiar with controllers and their expected responses
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help.html

    To get familiar with HTTPX check out their docs https://www.python-httpx.org/

    For Pi Web API Channels, use the WebsocketClient
    """

    def __init__(
        self,
        scheme: str = None,
        host: str = None,
        port: int = None,
        root: str = None,
        safe_chars: bytes = None,
        client: Union[ExClient, AsyncClient] = None,
        normalize_response_content: bool = False,
        auth: Auth = None,
        headers: Headers = None,
        cookies: CookieTypes = None,
        verify: bool = True,
        cert: CertTypes = None,
        http1: bool = True,
        http2: bool = False,
        proxies: ProxiesTypes = None,
        mounts: Mapping[str, AsyncBaseTransport] = None,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
        follow_redirects: bool = False,
        limits: Limits = DEFAULT_LIMITS,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        event_hooks: Mapping[str, List[Callable]] = None,
        transport: AsyncBaseTransport = None,
        app: Callable = None,
        trust_env: bool = True,
    ) -> None:
        
        self.scheme = scheme
        self.host = host
        self.port = port
        self.root = root or "/"
        self.safe_chars = safe_chars
        self.client = client or ExClient
        self.normalize_response_content = normalize_response_content
        self.has_base_url = False
        self._init_client(
            auth=auth,
            headers=headers,
            cookies=cookies,
            verify=verify,
            cert=cert,
            http1=http1,
            http2=http2,
            proxies=proxies,
            mounts=mounts,
            timeout=timeout,
            follow_redirects=follow_redirects,
            limits=limits,
            max_redirects=max_redirects,
            event_hooks=event_hooks,
            transport=transport,
            app=app,
            trust_env=trust_env
        )

    async def request(
        self,
        request: APIRequest,
        *,
        headers: HeaderTypes = None,
        auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: dict = None,
    ) -> APIResponse:

        """Send request to Pi Web API server, returns an APIResponse instance"""

        if request.protocol == "Websocket":
            raise RuntimeError(
                f"{self.__class__.__name__} does not support the websocket protocol"
            )

        url = request.raw_path if self.has_base_url else request.absolute_url
        request_to_send = self.client.build_request(
            method=request.method,
            url=url,
            json=request.body,
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
            raise HTTPClientError() from err
        try:
            content = orjson.loads(response.content)
        except orjson.JSONDecodeError:
            content = {
                "Errors": "Unable to parse response content",
                "ResponseContent": response.content.decode()
            }
        return APIResponse(
            status_code=response.status_code,
            url=response.url,
            headers=response.headers,
            normalize = self.normalize_response_content,
            **content
        )
        

    async def get(
        self,
        resource: BaseController,
        *,
        scheme: str = None,
        host: str = None,
        port: str = None,
        root: str = None,
        headers: HeaderTypes = None,
        auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: dict = None,
    ) -> APIResponse:

        """
        Construct and send GET request from BaseController instance, returns an
        APIResponse instance
        """

        self._verify_request(
            "GET",
            resource,
            scheme,
            host
        )
        root = root or self.root
        request: APIRequest = resource.build_request(scheme=scheme, host=host, port=port, root=root)
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
        resource: BaseController,
        *,
        scheme: str = None,
        host: str = None,
        port: str = None,
        root: str = None,
        headers: HeaderTypes = None,
        auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: dict = None
    ) -> APIResponse:
        
        """
        Construct and send POST request from BaseController instance, returns an
        APIResponse instance
        """

        self._verify_request(
            "POST",
            resource,
            scheme,
            host
        )
        root = root or self.root
        request: APIRequest = resource.build_request(scheme=scheme, host=host, port=port, root=root)
        return await self.request(
            request,
            headers=headers,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions
        )

    async def put(
        self,
        resource: BaseController,
        *,
        scheme: str = None,
        host: str = None,
        port: str = None,
        root: str = None,
        headers: HeaderTypes = None,
        auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: dict = None
    ) -> APIResponse:
        
        """
        Construct and send PUT request from BaseController instance, returns an
        APIResponse instance
        """

        self._verify_request(
            "PUT",
            resource,
            scheme,
            host
        )
        root = root or self.root
        request: APIRequest = resource.build_request(scheme=scheme, host=host, port=port, root=root)
        return await self.request(
            request,
            headers=headers,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions
        )

    async def patch(
        self,
        resource: BaseController,
        *,
        scheme: str = None,
        host: str = None,
        port: str = None,
        root: str = None,
        headers: HeaderTypes = None,
        auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: dict = None
    ) -> APIResponse:

        """
        Construct and send PATCH request from BaseController instance, returns an
        APIResponse instance
        """
        
        self._verify_request(
            "PATCH",
            resource,
            scheme,
            host
        )
        root = root or self.root
        request: APIRequest = resource.build_request(scheme=scheme, host=host, port=port, root=root)
        return await self.request(
            request,
            headers=headers,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions
        )

    async def delete(
        self,
        resource: BaseController,
        *,
        scheme: str = None,
        host: str = None,
        port: str = None,
        root: str = None,
        headers: HeaderTypes = None,
        auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: dict = None
    ) -> APIResponse:

        """
        Construct and send DELETE request from BaseController instance, returns an
        APIResponse instance
        """
        
        self._verify_request(
            "DELETE",
            resource,
            scheme,
            host
        )
        root = root or self.root
        request: APIRequest = resource.build_request(scheme=scheme, host=host, port=port, root=root)
        return await self.request(
            request,
            headers=headers,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions
        )

    def _init_client(
        self,
        auth: Auth = None,
        headers: Headers = None,
        cookies: CookieTypes = None,
        verify: bool = True,
        cert: CertTypes = None,
        http1: bool = True,
        http2: bool = False,
        proxies: ProxiesTypes = None,
        mounts: Mapping[str, AsyncBaseTransport] = None,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
        follow_redirects: bool = False,
        limits: Limits = DEFAULT_LIMITS,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        event_hooks: Mapping[str, List[Callable]] = None,
        transport: AsyncBaseTransport = None,
        app: Callable = None,
        trust_env: bool = True
    ) -> None:

        """Initialize httpx/httpx_extensions client instance"""

        if not self.client is ExClient and not self.client is AsyncClient:
            raise ValueError(f"Invalid client: {self.client.__class__.__name__}")
        
        base_url = self._get_base_url()
        
        # use event hook system to allow users to decide which characters to % encode
        event_hooks = {} if event_hooks is None else event_hooks
        if self.safe_chars:
            if not isinstance(self.safe_chars, str):
                raise TypeError(
                    f"Invalid type for 'safe_chars'. Expected str, got {type(self.safe_chars)}"
                )
            hook = functools.partial(use_safe_url_hook, self.safe_chars)
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
        
        if self.client is ExClient:
            self.client(
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
                base_url=base_url,
                transport=transport,
                trust_env=trust_env
            )
        else:
            self.client(
                auth=auth,
                headers=headers,
                cookies=cookies,
                verify=verify,
                cert=cert,
                http1=http1,
                http2=http2,
                proxies=proxies,
                mounts=mounts,
                timeout=timeout,
                follow_redirects=follow_redirects,
                limits=limits,
                max_redirects=max_redirects,
                event_hooks=event_hooks,
                base_url=base_url,
                transport=transport,
                app=app,
                trust_env=trust_env
            )
    
    def _get_base_url(self):
        """Constructs a base URL to be used in the httpx/httx_extensions client instance"""
        if self.scheme is None or self.host is None:
            return ""
        elif self.port is None:
            self.has_base_url = True
            return f"{self.scheme}://{self.host}"
        else:
            self.has_base_url = True
            return f"{self.scheme}://{self.host}:{self.port}"

    def _verify_request(
        self,
        expected_method: str,
        resource: BaseController,
        scheme: str,
        host: str
    ) -> None:
        """
        Verifys the resource requested from a BaseController instance supports the HTTP method
        called by the user. Also checks to see if enough information is present to construct URL
        """
        if not isinstance(resource, BaseController):
            raise TypeError(f"'resource' must be instance of BaseController. Got {type(resource)}")
        if resource.method != expected_method:
            raise ValueError(f"Invalid method for resource. Must use '{resource.method}' request.")
        if not self.has_base_url and not scheme and not host:
            raise ValueError("Must specify a scheme and host")

    async def aclose(self):
        """Close client"""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] = None,
        exc_value: BaseException = None,
        traceback: TracebackType = None,
    ) -> None:
        await self.aclose()