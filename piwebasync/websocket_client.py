import asyncio
import functools
import uuid
from collections import deque
from typing import Any, Callable, Optional, Sequence

from websockets.datastructures import HeadersLike
from websockets.exceptions import ConnectionClosed
from websockets.extensions import ClientExtensionFactory
from websockets.legacy.client import Connect
from websockets.typing import LoggerLike, Origin, Subprotocol
from ws_auth import Auth, WebsocketAuthProtocol

from .api.models import APIRequest, APIResponse
from .api.controllers.base import BaseController
from .exceptions import MaxConnectionsReached, WebsocketClientError


class PIChannel:

    """Pass"""

    def __init__(
        self,
        connection_factory: functools.partial,
        reconnect: bool = False,
        queue: asyncio.Queue = None,
        loop: asyncio.AbstractEventLoop = None
    ) -> None:

        self.connection_factory = connection_factory
        self.reconnect = reconnect
        self.queue = queue
        self.buffer = deque()
        self.channel_open = asyncio.Event()
        self.close_channel = asyncio.Event()
        self.wait_channel_closed = None
        self._loop = loop or asyncio.get_event_loop()
        self._id = uuid.uuid4().hex

    async def start(self, request: APIRequest) -> None:
        if self.reconnect:
            self._loop.create_task(self.open_reconnect_channel(request))
        else:
            self._loop.create_task(self.open_channel(request))

    async def open_channel(self, request: APIRequest) -> None:
        wait_channel_closed = self._loop.create_future()
        self.wait_channel_closed = wait_channel_closed
        async with self.connection_factory(APIRequest.absolute_url) as connection:
            self.data_transfer_task = self._loop.create_task(self.data_transfer(connection))
            await wait_channel_closed()

    async def open_reconnect_channel(self, request: APIRequest) -> None:
        wait_channel_closed = self._loop.create_future()
        self.wait_channel_closed = wait_channel_closed
        async for connection in self.connection_factory(request.absolute_url):
            if self.close_channel.is_set():
                break
            self.data_transfer_task = self._loop.create_task(self.data_transfer(connection))
            await wait_channel_closed()
            continue

    async def data_transfer(self, connection: WebsocketAuthProtocol) -> None:
        self.channel_open.set()
        while True:
            try:
                data = await connection.recv()
            except (ConnectionClosed, asyncio.CancelledError):
                self.channel_open.clear()
                if self.wait_channel_closed is not None:
                    wait_channel_closed = self.wait_channel_closed
                    wait_channel_closed.set_result(None)
                break
            


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
            Connect,
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
    ) -> PIChannel:
        """Pass"""
        if len(self._connections) >= self.MAX_CONNECTIONS:
            raise MaxConnectionsReached(
                "Maximum simultaneous connections opened. You can add "
                "additional streams to an existing connection by using "
                "the .update() method on a PIChannel object"
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
        """Pass"""
        if request.protocol != "Websocket":
            raise ValueError(
                f"Invalid protocol {request.protocol} for {self.__class__.__name__}"
            )
        connection_factory = self._connection_factory
        reconnect = self.reconnect
        loop = self._loop
        
    
    def _verify_request(
        self,
        expected_method: str,
        resource: BaseController,
        scheme: str,
        host: str
    ) -> None:
        """Pass"""
        if not isinstance(resource, BaseController):
            raise TypeError(f"'resource' must be instance of BaseController. Got {type(resource)}")
        if resource.method != expected_method:
            raise ValueError(f"Invalid method for resource. Must use '{resource.method}' request.")
        if not self.scheme and not self.host:
            if not scheme and not host:
                raise ValueError("Must specify a scheme and host")
        

