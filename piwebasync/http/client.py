import functools
from types import TracebackType
from typing import(
    Any,
    Callable,
    List,
    Mapping,
    Type,
    Union
)

import orjson
from httpx import (
    AsyncBaseTransport,
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

from ..api import APIRequest, HTTPResponse
from ..exceptions import HTTPClientError
from .hooks import use_safe_url_hook



class HTTPClient:

    """
    Asynchronous HTTP client for making requests to a Pi Web API server.
    Supports Kerberos and NTLM authentication

    Usage:
    >>> request = Controller(scheme, host, root=root).streams.get_end(webid)
    >>> async with piwebasync.HTTPClient() as client:
    >>>     response = await client.get(request)

    Args:
        - safe_chars (str): an optional string containing characters which
        should not be percent encoded when sending the request. Note that httpx's event
        hook system is used to wrap the default URL class before the request is sent
        and after the response is received. It will always be the first hook executed
        in both cases.

    The rest of arguments come the from the httpx_extensions.ExClient object...
    https://github.com/newvicx/httpx_extensions/blob/main/httpx_extensions/client.py

    The ExClient API mimics the HTTPX API and supports many of its features...
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
        limits: Limits = DEFAULT_LIMITS,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        event_hooks: Mapping[str, List[Callable]] = None,
        transport: AsyncBaseTransport = None,
        trust_env: bool = True,
    ) -> None:

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
    ) -> HTTPResponse:

        """
        Send request to Pi Web API server, returns an HTTPResponse instance

        Raises:
            - ValueError: invalid protocol for request
            - HTTPClientError: Error occurred in the underlying client object

        Returns:
            HTTPResponse
        """

        self._validate_protocol(request)
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
            raise HTTPClientError from err
        try:
            content = orjson.loads(response.content)
        except orjson.JSONDecodeError as err:
            content = {
                "Errors": "Unable to parse response content",
                "ResponseContent": response.content.decode(),
                "ErrorMessage": repr(err)
            }
        except BaseException as err:
            raise HTTPClientError from err

        return HTTPResponse(
            status_code=response.status_code,
            url=str(response.url),
            headers=response.headers,
            **content
        )
        

    async def get(
        self,
        request: APIRequest,
        *,
        headers: HeaderTypes = None,
        auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: dict = None,
    ) -> HTTPResponse:

        """
        Send GET request to Pi Web API server, returns an HTTPResponse instance

        Raises:
            - TypeError: request is not an instance of APIRequest
            - ValueError: client does not support this request
            - HTTPClientError: Error occurred in the underlying client object

        Returns:
            HTTPResponse
        """
        self._validate_method(request, "GET")
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
    ) -> HTTPResponse:
        
        """
        Send POST request to Pi Web API server, returns an HTTPResponse instance

        Raises:
            - TypeError: request is not an instance of APIRequest
            - ValueError: client does not support this request
            - HTTPClientError: Error occurred in the underlying client object

        Returns:
            HTTPResponse
        """
        self._validate_method(request, "POST")
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
    ) -> HTTPResponse:
        
        """
        Send PUT request to Pi Web API server, returns an HTTPResponse instance

        Raises:
            - TypeError: request is not an instance of APIRequest
            - ValueError: client does not support this request
            - HTTPClientError: Error occurred in the underlying client object

        Returns:
            HTTPResponse
        """
        self._validate_method(request, "PUT")
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
    ) -> HTTPResponse:

        """
        Send PATCH request to Pi Web API server, returns an HTTPResponse instance

        Raises:
            - TypeError: request is not an instance of APIRequest
            - ValueError: client does not support this request
            - HTTPClientError: Error occurred in the underlying client object

        Returns:
            HTTPResponse
        """
        self._validate_method(request, "PATCH")
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
    ) -> HTTPResponse:

        """
        Send DELETE request to Pi Web API server, returns an HTTPResponse instance

        Raises:
            - TypeError: request is not an instance of APIRequest
            - ValueError: client does not support this request
            - HTTPClientError: Error occurred in the underlying client object

        Returns:
            HTTPResponse
        """
        self._validate_method(request, "DELETE")
        return await self.request(
            request,
            headers=headers,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions
        )
    
    async def close(self) -> None:
        await self.client.aclose()

    def _configure_hooks(
        self,
        safe_chars: str = None,
        event_hooks: Mapping[str, List[Callable]] = None,
    ) -> Mapping[str, List[Callable]]:

        """
        Configure event hooks to support safe chars if specified
        
        Raises:
            - TypeError: safe chars are wrong type
        """
        
        event_hooks = event_hooks or {}
        if safe_chars:
            if not isinstance(safe_chars, str):
                raise TypeError(
                    f"Invalid type for 'safe_chars'. Expected str, got {type(self.safe_chars)}"
                )
            hook = functools.partial(use_safe_url_hook, safe_chars)
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

    def _validate_method(
        self,
        request: APIRequest,
        expected_method: str
    ) -> None:
        """
        Validate HTTP method of request

        Raises:
            - TypeError: request is not an APIRequest
            - ValueError: invalid HTTP method for request
        """
        
        if not isinstance(request, APIRequest):
            raise TypeError(f"'request' must be instance of APIRequest. Got {type(request)}")
        if request.method != expected_method:
            raise ValueError(
                f"Invalid method for request. Must use '{expected_method}' request. "
                f"Got '{request.method}'"
            )

    def _validate_protocol(self, request: APIRequest) -> None:
        """
        Validate request is an HTTP request
        
        Raises
            - TypeError: request is not an APIRequest
            - ValueError: invalid protocol for request
        """
        if not isinstance(request, APIRequest):
            raise TypeError(f"'request' must be instance of APIRequest. Got {type(request)}")
        if request.protocol != "HTTP":
            raise ValueError(
                f"Invalid protocol for {self.__class__.__name__}. Expected 'HTTP', "
                f"got '{request.protocol}'. If this is a websocket request, use the WebsocketClient"
            )

    async def __aenter__(self) -> "HTTPClient":
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] = None,
        exc_value: BaseException = None,
        traceback: TracebackType = None,
    ) -> None:
        await self.close()