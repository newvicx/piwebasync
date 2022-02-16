import asyncio
import json
from collections import deque
from contextlib import suppress
from types import TracebackType
from typing import(
    Any,
    Callable,
    Generator,
    Sequence,
    Type,
    Union
)

import orjson
import websockets
from websockets.datastructures import HeadersLike
from websockets.exceptions import ConnectionClosedError
from websockets.extensions import ClientExtensionFactory
from websockets.typing import LoggerLike, Origin, Subprotocol
from ws_auth import Auth, WebsocketAuthProtocol

from .api.controllers.base import BaseController
from .api.models import APIResponse
from .exceptions import ChannelClosed, SHUTDOWN



class Channel:

    """
    Open a websocket connection to PI Web API channel endpoint.
    Channel object mimics the websockets.Connect API but adds
    additional logic for auto reconnection and live updating of the
    websocket uri

    Usage:
    >>> async with Channel(resource) as channel:
    >>>     async for response in channel:
    >>>         process_response(response)

    Args:
        - resource (BaseController): PI Web API endpoint to connect to (Note that
        all controller objects must have the ``scheme`` and ``host`` parameters defined.
        Otherwise a ValueError will be raised)
        - reconnect (bool): Set true if websocket connection should continuously
        try reconnecting on a ConnectionClosedError
        - connect_timeout(float): timeout for connection to be established this should
        generally be longer than the open_timeout parameter but it is not required
        - normalize_response_content: if true converts top level keys in
        response content from camel case to snake case (WebId -> web_id). This can be useful
        in certain situations where you want to access attributes straigt from the response
        in a pythonic way. For example if normalize_response_content = True, you can access the
        WebId from a response (if it is in the top level of the body) as an attribute
        ``web_id = response.web_id``. If normalize_response_content = False you can
        still access the attribute using camel case ``web_id = response.WebId``
        - auth (Auth): httpx style auth flow for handling websocket handshake. Defaults to
        a "No Auth" scheme. See ws_auth README for more info
        - data_queue (asyncio.Queue): An optional queue to feed all responses to. If specified,
        any calls to .recv() will raise a RuntimeError

    The rest of the arguments come directly from the websockets.Connect object
    https://github.com/aaugustin/websockets/blob/main/src/websockets/legacy/client.py

    For more information on Channels in the PI Web API see...
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/topics/channels.html

    For all other PI Web API requests, use the HTTPClient
    """

    def __init__(
        self,
        resource: BaseController,
        reconnect: bool = False,
        connect_timeout: float = 15,
        normalize_response_content: bool = True,
        auth: Auth = None,
        create_protocol: Callable[[Any], WebsocketAuthProtocol] = None,
        logger: LoggerLike = None,
        compression: str = "deflate",
        origin: Origin = None,
        extensions: Sequence[ClientExtensionFactory] = None,
        subprotocols: Sequence[Subprotocol] = None,
        extra_headers: HeadersLike = None,
        open_timeout: float = 10,
        ping_interval: float = 20,
        ping_timeout: float = 20,
        close_timeout: float = None,
        max_size: int = 2 ** 20,
        max_queue: int = 2 ** 5,
        read_limit: int = 2 ** 16,
        write_limit: int = 2 ** 16,
        data_queue: asyncio.Queue = None,
        loop: asyncio.AbstractEventLoop = None,
        **kwargs: Any,
    ) -> None:

        self.url = resource.absolute_url
        self.reconnect = reconnect
        self.connect_timeout = connect_timeout
        self.normalize_response_content = normalize_response_content
        self.data_queue = data_queue
        self.connect_params = {
            "auth": auth,
            "create_protocol": create_protocol,
            "logger": logger,
            "compression": compression,
            "origin": origin,
            "extensions": extensions,
            "subprotocols": subprotocols,
            "extra_headers": extra_headers,
            "open_timeout": open_timeout,
            "ping_interval": ping_interval,
            "ping_timeout": ping_timeout,
            "close_timeout": close_timeout,
            "max_size": max_size,
            "max_queue": max_queue,
            "read_limit": read_limit,
            "write_limit": write_limit,
        }
        self.kwargs = kwargs
        self.loop = loop or asyncio.get_event_loop()
        self._buffer = deque()
        self._channel_closed = False
        self._channel_connection_task = None
        self._channel_open = asyncio.Event()
        self._pop_message_waiter = None
        self._shutdown_waiter = None
        self._transfer_data_task = None
        self._transfer_start_waiter = None
        self._updating = False

    async def update(self, resource: BaseController) -> None:

        """
        Update endpoint without "closing" channel. The response
        buffer is NOT cleared and the user can continue to receive
        messages. When the new connection is established, new responses
        will be representative of the updated endpoint. Any responses
        buffered previously will be represantive of the old endpoint

        Args:
            resource (BaseController): PI Web API endpoint to connect to

        Raises:
            ChannelClosed: Channel was closed by user or system
            asyncio.TimeoutError: Operation timed out trying to establish
            a new connection
        """

        try:
            self._updating = True
            if self._channel_closed:
                raise ChannelClosed("Channel closed")
            with suppress(Exception):
                await self._shutdown()
            self.url = resource.absolute_url
            await self._start()
        finally:
            self._updating = False

    async def recv(self) -> APIResponse:

        """
        Receive API response from buffer

        Raises:
            - ChannelClosed: Channel was closed by user or system
            - RuntimeError: .recv() was called from another coroutine OR
            user specified a data_queue to feed responses to when a message
            is received
        Returns:
            APIResponse
        """

        if self._channel_closed:
            raise ChannelClosed("Channel closed")
        if self._pop_message_waiter is not None:
            raise RuntimeError(
                "cannot call recv while another coroutine "
                "is already waiting for the next message"
            )
        if self.data_queue is not None:
            raise RuntimeError(
                "cannot call recv when messages are being "
                "being passed to a data queue"
            )

        while (len(self._buffer)) <= 0:
            await self._channel_open.wait()
            pop_message_waiter: asyncio.Future = self.loop.create_future()
            self._pop_message_waiter = pop_message_waiter
            try:
                # If asyncio.wait() is canceled, it doesn't cancel
                # pop_message_waiter or self.transfer_data_task.
                await asyncio.wait(
                    [pop_message_waiter, self._transfer_data_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
            finally:
                self._pop_message_waiter = None

            if not pop_message_waiter.done():
                # if channel_connection_task is running it is trying to reconnect
                if self._channel_connection_task.done():
                    # during channel update _channel_connection_task will be cancelled
                    # but the channel should not be closed
                    if not self._updating:
                        # should raise error that occurred in _channel_connection_task
                        # as a ConnectionClose error
                        await self.close()

        return self._buffer.popleft()

    async def close(self) -> None:

        """
        Close channel and clear buffer

        Raises:
            - ChannelClosed: channel closed as a result of an exception
            that occurred in _channel_connnection_task
        """
        
        self._channel_closed = True
        try:
            await self._shutdown()
        except Exception as err:
            raise ChannelClosed(
                "Channel closed as a direct result of the above exception"
            ) from err
        finally:
            self._buffer.clear()

    async def _start(self) -> None:
        
        """
        Start _channel_connection_task which opens channel. This method
        should not be cancelled
        
        Raises:
            - asyncio.TimeoutError: First connection not established in
            connect_timeout seconds
        """
        
        channel_connection_task = self.loop.create_task(self._run())
        transfer_start_waiter = self.loop.create_future()
        self._transfer_start_waiter = transfer_start_waiter
        
        try:
            await asyncio.shield(
                asyncio.wait_for(
                    transfer_start_waiter, self.connect_timeout
                )
            )
        except asyncio.TimeoutError:
            channel_connection_task.cancel()
            with suppress(asyncio.CancelledError):
                await channel_connection_task
            raise
        finally:
            self._transfer_start_waiter = None
        
        self._channel_connection_task = channel_connection_task

    async def _run(self) -> None:
        
        """
        Open channel connection. If reconnect=True, on an unexpected channel
        close, this method will attempt to reconnect the channel infinitely
        """
        
        async for protocol in websockets.connect(
            self.url, **self.connect_params, **self.kwargs
        ):
            self._channel_open.set()
            shutdown_waiter = self.loop.create_future()
            self._shutdown_waiter = shutdown_waiter
            transfer_data_task = self.loop.create_task(self._transfer_data(protocol))
            self._transfer_data_task = transfer_data_task
            try:
                await asyncio.wait(
                    [shutdown_waiter, transfer_data_task],
                    return_when=asyncio.FIRST_EXCEPTION
                )
            # _shutdown() called
            except SHUTDOWN:
                transfer_data_task.cancel()
                with suppress(asyncio.CancelledError):
                    await transfer_data_task
                return
            # Connection closed unexpectedly, check for reconnect
            except ConnectionClosedError:
                if self.reconnect:
                    continue
                raise
            # Unhandled exceptions in transfer data task are raised in _run()
            finally:
                self._channel_open.clear()
                self._shutdown_waiter = None

    async def _transfer_data(self, protocol: WebsocketAuthProtocol) -> None:
        
        """
        Receive messages from websocket connection forever, parse messages to
        APIResponse objects and either buffer the messages or pass to data_queue

        Args:
            protocol (WebsocketAuthProtocol): Websocket connection object
        """
        
        self._transfer_start_waiter.set_result(None)
        async for message in protocol:
            response = self._process_message(message)
            if self.data_queue is not None:
                await self.data_queue.put(response)
                continue
            self._buffer.append(response)
            if self._pop_message_waiter is not None:
                self._pop_message_waiter.set_result(None)
                self._pop_message_waiter = None

    def _process_message(self, message: Union[str, bytes]) -> APIResponse:
        
        """
        Parse message from websocket to APIResponse object

        Args:
            message (Union[str, bytes]): Raw message returned from websocket

        Returns:
            APIResponse: Formatted PI Web API response
        """
        
        try:
            content = json.loads(message) if isinstance(message, str) else orjson.loads(message)
        except (json.JSONDecodeError, orjson.JSONDecodeError):
            message = message if isinstance(message, str) else message.decode()
            content = {
                "Errors": "Unable to parse response content",
                "ResponseContent": message
            }
        return APIResponse(
            status_code=101,
            url=self.url,
            normalize=self.normalize_response_content,
            **content
        )
    
    async def _shutdown(self) -> None:
        
        """
        Shutdown websocket connection
        
        Raises:
            - ChannelClosedError: websocket connection closed unexpectedly
            and reconnect=False
            - Exception: Unhandled exception in _data_transfer_task
            - asyncio.CancelledError: _channel_connection_task was attempting to
            reconnect and was cancelled
        """
        
        try:
            if self._shutdown_waiter is not None:
                self._shutdown_waiter.set_exception(SHUTDOWN)
            # could be trying to reconnect
            elif not self._channel_connection_task.done():
                self._channel_connection_task.cancel()
            await self._channel_connection_task
        finally:
            self._channel_connection_task = None

    async def __aiter__(self):
        
        """
        Iterate on incoming responses

        Yields:
           APIResponse

         Raises:
            - ChannelClosed: Channel was closed by user or system
            - RuntimeError: channel was iterated from another coroutine OR
            user specified a data_queue to feed responses to when a message
            is received
        """
        
        while True:
            yield await self.recv()

    async def __aenter__(self) -> "Channel":
        return await self

    async def __aexit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        await self.close()

    # async with Channel(...) as channel
    # OR
    # try
    #   channel = await Channel(...)
    #       do something
    # finally:
    #   await channel.close()

    def __await__(self) -> Generator[Any, None, "Channel"]:
        # Create a suitable iterator by calling __await__ on a coroutine.
        return self.__await_impl__().__await__()

    async def __await_impl__(self) -> "Channel":
        await self._start()
        return self