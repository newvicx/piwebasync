import asyncio
import json
import logging
from collections import deque
from types import TracebackType
from typing import(
    Any,
    AsyncIterator,
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
from websockets.typing import Origin, Subprotocol
from ws_auth import Auth, WebsocketAuthProtocol

from ..api import APIRequest, WebsocketMessage
from ..exceptions import(
    ChannelClosedError,
    ChannelClosedOK,
    ChannelUpdateError,
    WatchdogTimeout
)


logger = logging.getLogger(__name__)


class WebsocketClient:

    """
    Asynchronous Websocket client to PI Web API channel endpoint.
    Supports Kerberos and NTLM authentication

    Usage:
    >>> request = Controller(scheme, host, root=root).streams.get_channel(webid)
    >>> async with WebsocketClient(request) as channel:
    >>>     async for response in channel:
    >>>         process_response(response)

    Args:
        - request (APIRequest): PI Web API endpoint to connect to
        - reconnect (bool): if true, the channel will try and reconnect on 
        a ConnectionClosedError
        - open_timeout(float): timeout for channel to be opened
        - dead_channel_timeout (float): timeout for channel to be considered "dead". If
        reconnect=True, a watchdog task will monitor the channel and close the channel
        if the channel is unable to reconnect in the allotted time. Set to None for no timeout
        - auth (Auth): httpx style auth flow for handling websocket handshake. Defaults to
        a "No Auth" scheme. See ws_auth README for more info

    The rest of the arguments come directly from the websockets.Connect object...
    https://github.com/aaugustin/websockets/blob/main/src/websockets/legacy/client.py

    For more information on Channels in the PI Web API see...
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/topics/channels.html

    For all other PI Web API requests, use the HTTPClient
    """

    def __init__(
        self,
        request: APIRequest,
        *,
        create_protocol: Callable[[Any], WebsocketAuthProtocol] = None,
        auth: Auth = None,
        compression: str = "deflate",
        origin: Origin = None,
        extensions: Sequence[ClientExtensionFactory] = None,
        subprotocols: Sequence[Subprotocol] = None,
        extra_headers: HeadersLike = None,
        open_timeout: float = 10,
        reconnect: bool = False,
        dead_channel_timeout: float = 3600,
        ping_interval: float = 20,
        ping_timeout: float = 20,
        close_timeout: float = 3,
        max_size: int = 2**20,
        max_queue: int = 2**5,
        read_limit: int = 2**16,
        write_limit: int = 2**16,
        loop: asyncio.AbstractEventLoop = None
    ) -> None:

        self._verify_request(request)
        self.url = request.absolute_url
        self._reconnect = reconnect
        self._open_timeout = open_timeout
        self._dead_channel_timeout = dead_channel_timeout
        self._ws_connect_params = dict(
            auth=auth,
            create_protocol=create_protocol,
            compression=compression,
            origin=origin,
            extensions=extensions,
            subprotocols=subprotocols,
            extra_headers=extra_headers,
            open_timeout=None,
            ping_interval=ping_interval,
            ping_timeout=ping_timeout,
            close_timeout=close_timeout,
            max_size=max_size,
            max_queue=max_queue,
            read_limit=read_limit,
            write_limit=write_limit,
        )
        self._loop = loop or asyncio.get_event_loop()

        self._buffer = deque()
        self._channel_exc: BaseException = None
        self._channel_open_event: asyncio.Event = asyncio.Event()
        self._close_channel_task: asyncio.Task = None
        self._close_channel_waiter: asyncio.Future = None
        self._no_data_transfer_event: asyncio.Event = asyncio.Event()
        self._pop_message_waiter: asyncio.Future = None
        self._run_channel_task: asyncio.Task = None
        self._update_lock: asyncio.Lock = asyncio.Lock()
        self._waiting_recv: bool = False
        self._waiting_update: bool = False
        self._watchdog_task: asyncio.Task = None

    @property
    def is_closed(self):
        """
        `True` when channel is closed; `False` otherwise

        The channel is closed when the _close_channel_task is done.
        """
        if self._close_channel_task is not None:
            return self._close_channel_task.done()
        return True

    @property
    def is_closing(self):
        """
        `True` when channel is closing; `False` otherwise

        The channel is closed when the _close_channel_waiter is done.
        The _run_channel_task is being awaited when the channel is closing
        """
        if self._close_channel_waiter is not None:
            return self._close_channel_waiter.done()
        return True

    @property
    def is_open(self):
        """
        `True` when channel is open; `False` otherwise

        The channel is considered open when the underlying websocket protocol
        instance is open and can receive messages
        """
        if self._run_channel_task is not None:
            return (
                not self._run_channel_task.done() and
                not self._no_data_transfer_event.is_set()
            )
        return False

    @property
    def is_reconnecting(self):
        """
        `True` when channel is reconnecting; `False` otherwise

        The channel is considered reconnecting when the underlying websocket protocol
        instance is closed but the _run_channel_task is not done
        """
        if self._run_channel_task is not None:
            return (
                not self._run_channel_task.done() and
                self._no_data_transfer_event.is_set()
            )
        return False

    async def recv(self) -> WebsocketMessage:
        """
        Receive the next message from the buffer

        When the connection is closed, `recv` raises
        `~piwebasync.exceptions.ChannelClosed`. Specifically, it
        raises `~piwebasync.exceptions.ChannelClosedOK` after a normal
        connection closure and
        `~piwebasync.exceptions.ChannelClosedError` after a protocol
        error or a network failure. This is how you detect the end of the
        message stream.

        Canceling `recv` is safe. There's no risk of losing the next
        message. The next invocation of `recv` will return it.

        Returns
            - WebsocketMessage

        Raises
            - ChannelClosed: when the connection is closed.
            - RuntimeError: if two coroutines call `recv` concurrently.
        """

        if self._waiting_recv:
            raise RuntimeError(
                "cannot call recv while another coroutine "
                "is already waiting for the next message"
            )
        
        while (len(self._buffer)) <= 0:
            self._waiting_recv = True
            try:
                # wait for channel open
                if not self._channel_open_event.is_set():
                    channel_open_waiter = self._loop.create_task(self._channel_open_event.wait())
                    try:
                        await asyncio.wait(
                            [channel_open_waiter, self._close_channel_waiter],
                            return_when=asyncio.FIRST_COMPLETED
                        )
                        if not channel_open_waiter.done():
                            # channel is closing, raise appropriate error
                            await self._ensure_open()
                    finally:
                        if not channel_open_waiter.done():
                            channel_open_waiter.cancel()
                # wait for new data
                pop_message_waiter: asyncio.Future = self._loop.create_future()
                self._pop_message_waiter = pop_message_waiter
                data_transfer_waiter = self._loop.create_task(self._no_data_transfer_event.wait())
                try:
                    await asyncio.wait(
                        [pop_message_waiter, data_transfer_waiter],
                        return_when=asyncio.FIRST_COMPLETED
                    )
                finally:
                    if not data_transfer_waiter.done():
                        data_transfer_waiter.cancel()
                    self._pop_message_waiter = None
                # if data transfer finished first, ensure channel is not closing
                # if channel is reconnecting, continue
                # if closing, raise the appropriate error
                # if updating, block till update process completes
                if not pop_message_waiter.done():
                    await self._ensure_open()
            finally:
                self._waiting_recv = False
        
        return self._buffer.popleft()

    async def update(self, request: APIRequest) -> None:
        """
        Update Channel endpoint
        
        This method does not interrupt :meth:`recv`.
        Any messages already in the client buffer will remain
        there. New messages will reflect the updated endpoint
        accordingly. If :meth:`update` fails with a ChannelUpdateError,
        the channel will close

        Args:
            - request (APIRequest): The new endpoint to
            connect to
        Raises:
            - ChannelUpdateError: Unable to establish connection
            to new endpoint
            - ChannelClosed: The channel is closed
            - ValueError: Request is invalid
            - RuntimeError: if two coroutines call :meth:`update`
            concurrently
        """
        
        if self._waiting_update:
            raise RuntimeError(
                "Cannot call update while another coroutine "
                "is already waiting to update client"
            )

        self._waiting_update = True
        try:
            await self._ensure_open()
            self._verify_request(request)
            self.url = request.absolute_url
            async with self._update_lock:
                logger.debug("updating channel endpoint")
                self._close_channel_waiter.set_result(None)
                await self._close_channel_task
                try:
                    await self._start()
                    await asyncio.sleep(0)
                except asyncio.TimeoutError as err:
                    exc = ChannelUpdateError(
                        "Unable to establish new connection"
                    )
                    exc.__cause__ = err
                    self._set_channel_exc(exc)
                    self._close_channel_task = None
                    logger.debug("unable to update channel. Channel is closed")
                    raise exc
        finally:
            self._waiting_update = False

    async def close(self) -> None:
        """
        Close the client
        
        Execute closing sequence. Calls to `recv` after the closing
        sequence has started will raise ChannelClosed
        """
        try:
            logger.debug("closing channel")
            if not self.is_closed:
                if not self.is_closing:
                    logger.debug("signaling close channel task")
                    self._close_channel_waiter.set_result(None)
                await self._close_channel_task
                logger.debug("channel closed")
        finally:
            self._close_channel_task = None

    async def _ensure_open(self) -> None:
        """
        Check if channel is open

        If `update` is called, the channel will appear to be closed.
        Calls to `recv` will wait to aquire the lock indicating the
        update process finished before assessing the state of the channel.

        If an error occurred during channel operation, this method
        will raise ~piwebasync.exceptions.ChannelClosedError otherwise,
        if the channel is closed or closing it will raise
        ~piwebasync.exceptions.ChannelClosedOK

        Raises:
            - ChannelClosed
        """
        
        async with self._update_lock:
            if self.is_closed or self.is_closing:
                self._raise_channel_exc()

    async def _start(self) -> None:
        """
        Establish channel connection

        Raises:
            - asyncio.TimeoutError: Operation timed out trying to
            establish connection
            - RuntimeError: Attempted to open channel that is not
            closed or `close` was not called
        """
        if not self.is_closed:
            raise RuntimeError(
                "Cannot open new connection. Client is not closed"
            )

        self._channel_exc = None
        run_channel_task = self._loop.create_task(self._run())
        try:
            await asyncio.wait_for(
                self._channel_open_event.wait(),
                self._open_timeout
            )
        except asyncio.TimeoutError:
            run_channel_task.cancel()
            raise
        # connection established
        self._run_channel_task = run_channel_task
        self._close_channel_task = self._loop.create_task(self._close_channel())
        self._watchdog_task = self._loop.create_task(self._watchdog())
        logger.debug("channel open, all tasks started")
        # ensures all tasks start before recv is called which led to
        # deadlocks in testing
        await asyncio.sleep(0)

    async def _run(self) -> None:
        """
        Run websocket protocol and data transfer in a loop

        This task will continuously attempt to establish a websocket
        connection to the channel endpoint. Once a connection is established
        it will begin a data transfer task to receive messages, process them,
        and place them in a buffer. If the websocket connection is closed via
        a protocol failure, network failure, or message processing failure; the
        channel may attempt to reconnect otherwise it will break out of the loop.
        The completion of the this task by an exception will trigger the closing
        of the client instance. This task is designed to be cancelled by
        `close_channel` during a normal close procedure
        """
        try:
            async for protocol in websockets.connect(self.url, **self._ws_connect_params):
                logger.debug("channel opened")
                self._channel_open_event.set()
                try:
                    await self._transfer_data(protocol)
                # websocket connection was lost
                except ConnectionClosedError as err:
                    logger.debug("protocol or network error ocurred", exc_info=True)
                    if self._reconnect:
                        logger.debug("attempting to reconnect")
                        continue
                    self._set_channel_exc(err)
                    break
                # drop when websockets no longer supports python < 3.8
                except asyncio.CancelledError:
                    raise
                # an exception was raised processing message
                except Exception as err:
                    logger.debug("unhandled exception in _transfer_data", exc_info=True)
                    if self._reconnect:
                        logger.debug("attempting to reconnect")
                        continue
                    await protocol.close()
                    self._set_channel_exc(err)
                    break
                finally:
                    self._channel_open_event.clear()
        except asyncio.CancelledError:
            pass

    async def _close_channel(self) -> None:
        """
        Close the channel

        This task is started after the first connection to the
        channel endpoint is established. It ensures `run channel task`
        finishes
        """

        close_channel_waiter = self._loop.create_future()
        self._close_channel_waiter = close_channel_waiter
        try:
            await asyncio.wait(
                [close_channel_waiter, self._run_channel_task],
                return_when=asyncio.FIRST_COMPLETED
            )
        except asyncio.CancelledError:
            pass
        finally:
            self._close_channel_waiter = None
        # if wait was cancelled or close_channel_waiter finished
        # first, cancel _run_channel_task
        if not self._run_channel_task.done():
            self._run_channel_task.cancel()
        await asyncio.shield(self._run_channel_task)

    async def _transfer_data(self, protocol: WebsocketAuthProtocol) -> None:
        """
        Receive and process messages from websocket connection. Place processed
        messages in buffer

        This method will continuously receive messages from an open websocket
        connection. It is always awaited on by the `run` method. Any that ocurrs
        will propagate to and be handled by the parent task. Flow control is
        handled at the protocol level
        """

        try:
            self._no_data_transfer_event.clear()
            async for message in protocol:
                websocket_message = self._process_message(message)
                logger.debug("message received for endpoint %s", websocket_message.url)
                self._buffer.append(websocket_message)
                # wake up receiver if waiting for a message
                if self._pop_message_waiter is not None:
                    logger.debug("waking receiver")
                    self._pop_message_waiter.set_result(None)
                    self._pop_message_waiter = None
        finally:
            self._no_data_transfer_event.set()

    def _process_message(self, message: Union[bytes, str]) -> WebsocketMessage:
        """
        Parse message from websocket to WebsocketMessage object

        Args:
            message (Union[str, bytes]): Raw message returned from websocket

        Returns:
            WebsocketMessage: Formatted PI Web API channel message
        """
        
        try:
            content = orjson.loads(message) if isinstance(message, bytes) else json.loads(message)
        except (json.JSONDecodeError, orjson.JSONDecodeError) as err:
            message = message.decode() if isinstance(message, bytes) else message
            content = {
                "Errors": "Unable to parse response content",
                "ResponseContent": message,
                "ErrorMessage": repr(err)
            }    
        return WebsocketMessage(
            url=self.url,
            **content
        )
    
    async def _watchdog(self) -> None:
        """
        Oversee channel reconnects. Close the channel if unable to reconnect

        If the watchdog times out it will start the channel closing process
        and set the `channel_exc` property. Calls to `recv` will raise a
        `~piwebasync.exceptions.ChannelClosedError` resulting from
        `~piwebasync.exceptions.WatchdogTimeout`
        """
        if self._reconnect:
            logger.debug("watchdog active")
            drops = 0
            while True:
                if self.is_closed or self.is_closing:
                    break
                try:
                    try:
                        logger.debug("waiting for channel open. Drops: %i", drops)
                        await asyncio.wait_for(
                            self._channel_open_event.wait(),
                            self._dead_channel_timeout
                        )
                    except asyncio.TimeoutError as err:
                        exc = WatchdogTimeout()
                        exc.__cause__ = err
                        self._set_channel_exc(exc)
                        self._close_channel_waiter.set_result(None)
                        break
                    await self._no_data_transfer_event.wait()
                    drops += 1
                except asyncio.CancelledError:
                    pass
    
    def _set_channel_exc(self, exc: BaseException) -> None:
        """
        Chain multiple exceptions
        """
        if self._channel_exc is not None:
            exc.__cause__ = self._channel_exc
        self._channel_exc = exc
    
    def _raise_channel_exc(self) -> None:
        """
        Raise channel exception
        """
        if self._channel_exc is None:
            raise ChannelClosedOK("Channel closed")
        raise ChannelClosedError(
            "Channel closed due to another exception"
        ) from self._channel_exc

    def _verify_request(
        self,
        request: APIRequest
    ) -> None:
        """
        Validates request type and also validates client can handle request

        Raises:
            - TypeError: request is not an instance of APIRequest
            - ValueError: client does not support this request
        """
        
        if not isinstance(request, APIRequest):
            raise TypeError(f"'request' must be instance of APIRequest. Got {type(request)}")
        if request.method != "GET":
            raise ValueError(
                f"Invalid method for request. Must use 'GET' request. "
                f"Got '{request.method}'"
            )
        if request.protocol != "Websocket":
            raise ValueError(
                f"Invalid protocol for {self.__class__.__name__}. Expected 'Websocket', "
                f"got '{request.protocol}'. If this is a HTTP request, use the HTTPClient"
            )

    async def __aiter__(self) -> AsyncIterator[WebsocketMessage]:
        
        """
        Iterate on incoming messages

        Yields:
           WebsocketMessage

        Raises:
            Raises
            - ChannelClosed: when the connection is closed.
            - RuntimeError: if two coroutines call `recv` concurrently.
        """
        
        while True:
            yield await self.recv()

    async def __aenter__(self) -> "WebsocketClient":
        return await self

    async def __aexit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        await self.close()

    # async with WebsocketClient(...) as channel
    # OR
    # try
    #   channel = await WebsocketClient(...)
    #   do something
    # finally:
    #   await channel.close()

    def __await__(self) -> Generator[Any, None, "WebsocketClient"]:
        # Create a suitable iterator by calling __await__ on a coroutine.
        return self.__await_impl__().__await__()

    async def __await_impl__(self) -> "WebsocketClient":
        await self._start()
        return self