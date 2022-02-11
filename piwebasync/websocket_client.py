import asyncio
import functools
from collections import deque
from typing import Any, Callable, Optional, Sequence, Union

import websockets
import ws_auth
from httpx._client import UseClientDefault, USE_CLIENT_DEFAULT
from websockets.datastructures import HeadersLike
from websockets.extensions import ClientExtensionFactory
from websockets.legacy.client import Connect
from websockets.typing import LoggerLike, Origin, Subprotocol
from ws_auth import Auth, WebsocketAuthProtocol

from .api.models import APIRequest, APIResponse
from .api.controllers.base import BaseController
from .exceptions import MaxConnectionsReached, WebsocketClientError


class WebsocketClient:

    """
    A wesocket client for use with PI Web API ``Channels``
    The API is based off the websockets API but can transparently
    handle events such as reconnects and wsuri updates

    For more information on PI Web API Channels see the API reference
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/topics/channels.html
    
    For more information on the websockets package check out the docs
    https://websockets.readthedocs.io/en/stable/
    
    For more information on the websocket protocol see the RFC
    https://datatracker.ietf.org/doc/html/rfc6455
    """

    MAX_CONNECTIONS = 100

    def __init__(
        self,
        scheme: str = None,
        host: str = None,
        port: int = None,
        root: str = None,
        reconnect: bool = False,
        auth: Auth = None,
        create_protocol: Callable[[Any], WebsocketAuthProtocol] = None,
        logger: Optional[LoggerLike] = None,
        compression: Optional[str] = "deflate",
        origin: Optional[Origin] = None,
        extensions: Optional[Sequence[ClientExtensionFactory]] = None,
        subprotocols: Optional[Sequence[Subprotocol]] = None,
        extra_headers: Optional[HeadersLike] = None,
        open_timeout: Optional[float] = 10,
        ping_interval: Optional[float] = 20,
        ping_timeout: Optional[float] = 20,
        close_timeout: Optional[float] = None,
        max_size: Optional[int] = 2 ** 20,
        max_queue: Optional[int] = 2 ** 5,
        read_limit: int = 2 ** 16,
        write_limit: int = 2 ** 16,
        loop: asyncio.AbstractEventLoop = None,
        **kwargs: Any,
    ) -> None:

        self.scheme = scheme
        self.host = host
        self.port = port
        self.root = root
        self.reconnect = reconnect
        self._connection_factory = functools.partial(
            websockets.connect,
            create_protocol=create_protocol,
            auth=auth,
            logger=logger,
            compression=compression,
            origin=origin,
            extensions=extensions,
            subprotocols=subprotocols,
            extra_headers=extra_headers,
            open_timeout=open_timeout,
            ping_interval=ping_interval,
            ping_timeout=ping_timeout,
            close_timeout=close_timeout,
            max_size=max_size,
            max_queue=max_queue,
            read_limit=read_limit,
            write_limit=write_limit,
            **kwargs
        )
        self._connections = []
        self._loop = loop or asyncio.get_event_loop()
    
    async def connect(
        self,
        resource: BaseController,
        *,
        scheme: str = None,
        host: str = None,
        port: str = None,
        root: str = None
    ):
        
        if len(self._connections) >= self.MAX_CONNECTIONS:
            raise MaxConnectionsReached(
                "Maximum simultaneous connections opened. You can add "
                "additional streams to an existing connection by using "
                "the .update() method on PIChannel object"
            )
        self._verify_request(
            "GET",
            resource,
            scheme,
            host
        )
        scheme = scheme or self.scheme
        host = host or self.host
        port = port or self.port
        root = root or self.root
        request: APIRequest = resource.build_request(scheme=scheme, host=host, port=port, root=root)
        return await self._create_channel(request)

    async def _create_channel(self, request: APIRequest) -> PIChannel:

        if request.protocol != "Websocket":
            raise ValueError(
                f"Invalid protocol {request.protocol} for {self.__class__.__name__}"
            )
        connection_factory = self._connection_factory
        reconnect = self.reconnect
        loop = self._loop
        return await PIChannel.connect(request, connection_factory, reconnect, loop)
    
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
        if not self.scheme and not self.host:
            if not scheme and not host:
                raise ValueError("Must specify a scheme and host")


class PIChannel:

    def __init__(
        self,
        protocol: WebsocketAuthProtocol,
        request: APIRequest,
        connection_factory: Connect,
        reconnect: bool,
        loop: asyncio.AbstractEventLoop
    ) -> None:

        self.protocol = protocol
        self.request = request
        self.connection_factory = connection_factory
        self.reconnect = reconnect
        self._buffer = deque()
        self._loop = loop

    @classmethod
    async def connect(
        cls,
        request: APIRequest,
        connection_factory: Connect,
        reconnect: bool,
        loop: asyncio.AbstractEventLoop
    ) -> "PIChannel":
        
        uri = request.absolute_url
        protocol = await connection_factory(uri)
        

