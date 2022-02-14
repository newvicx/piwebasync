import asyncio
import functools
import json
import uuid
from collections import deque
from typing import Any, Callable, Optional, Sequence

import orjson
from websockets.datastructures import HeadersLike
from websockets.exceptions import ConnectionClosedOK
from websockets.extensions import ClientExtensionFactory
from websockets.legacy.client import Connect
from websockets.typing import LoggerLike, Origin, Subprotocol
from ws_auth import Auth, WebsocketAuthProtocol

from .api.models import APIRequest, APIResponse
from .api.controllers.base import BaseController
from .exceptions import BufferConsumed, MaxConnectionsReached


class PIChannel:

    """Pass"""

    def __init__(
        self,
        connection_factory: functools.partial,
        reconnect: bool = False,
        normalize_response_content: bool = False,
        loop: asyncio.AbstractEventLoop = None
    ) -> None:

        self.connection_factory = connection_factory
        self.reconnect = reconnect
        self.normalize_response_content = normalize_response_content
        self.loop = loop or asyncio.get_event_loop()
        self.buffer = deque()
        self.channel_id = uuid.uuid4().hex
        self.channel_closed = asyncio.Event()
        self.channel_open = asyncio.Event()
        self.channel_closed_waiter = None
        self.pop_message_waiter = None
        self.data_transfer_task = None

    async def start(self, url: str, timeout: Union[int, float] = None) -> None:
        if self.wait_channel_closed is not None:
            raise ConnectionResetError("Channel already open")
        self.channel_closed.clear()
        self.wait_channel_closed = self.loop.create_future()
        self.loop.create_task(self.open_channel(url))
        try:
            await self.channel_open.wait(timeout)
        except asyncio.CancelledError:
            pass

    async def open_channel(self, url: str) -> None:
        async for connection in self.connection_factory(url):
            channel_closed_waiter = self.loop.create_future()
            self.channel_closed_waiter = channel_closed_waiter
            data_transfer_task = self.loop.create_task(self.data_transfer(connection, url))
            self.data_transfer_task = data_transfer_task
            try:
                await asyncio.wait(
                    [channel_closed_waiter, data_transfer_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
            finally:
                if not data_transfer_task.done():
                    data_transfer_task.cancel()
                if not channel_closed_waiter.done():
                    channel_closed_waiter.set_result(None)
                self.channel_closed_waiter = None
                self.data_transfer_task = None
                await connection.close()
            if self.channel_close_event.is_set():
                break
            if not self.reconnect:
                break
            continue
        self.channel_closed.set()
        self.wait_channel_closed.set_result(None)

    async def data_transfer(self, connection: WebsocketAuthProtocol, url: str) -> None:
        try:
            self.channel_open.set()
            async for message in connection:
                try:
                    content = json.loads(message) if isinstance(message, str) else orjson.loads(message)
                except json.JSONDecodeError:
                    message = message if isinstance(message, str) else message.decode()
                    content = {
                        "Errors": "Unable to parse response content",
                        "ResponseContent": message
                    }
                response = APIResponse(
                    status_code=101,
                    url=url,
                    normalize=self.normalize,
                    **content
                )
                self.buffer.append(response)
                if self.pop_message_waiter is not None:
                    self.pop_message_waiter.set_result(None)
                    self.pop_message_waiter = None
        except asyncio.CancelledError:
            pass
        except ConnectionClosedOK:
            pass
        finally:
            self.channel_open.clear()

    async def close(self) -> None:
        await self.shutdown()
        self.buffer.clear()

    async def shutdown(self) -> None:
        self.channel_closed.set()
        if self.channel_closed_waiter is not None:
            self.channel_closed_waiter.set_result(None)
        await self.wait_channel_closed
    
    # Copied from websockets .recv()
    async def recv(self) -> APIResponse:
        if self.pop_message_waiter is not None:
            raise RuntimeError(
                "cannot call recv while another coroutine "
                "is already waiting for the next message"
            )
        if len(self.buffer) <= 0 and self.channel_closed.is_set():
            raise BufferConsumed()
        while len(self.buffer) <= 0:
            pop_message_waiter = self.loop.create_future()
            self.pop_message_waiter = pop_message_waiter
            try:
                # If asyncio.wait() is canceled, it doesn't cancel
                # pop_message_waiter and self.transfer_data_task.
                await asyncio.wait(
                    [pop_message_waiter, self.transfer_data_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
            finally:
                self._pop_message_waiter = None
            
            if not pop_message_waiter.done():
                return None
        
        response = self.buffer.popleft()
        return response

    async def update(self, url: str) -> None:
        if not self.channel_closed.is_set():
            await self.shutdown()
        await self.start(url)

    
    async def __aiter__(self):
        while True:
            yield await self.recv()


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
        

