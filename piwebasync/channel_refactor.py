import asyncio
import json
import logging
import random
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
from websockets.exceptions import ConnectionClosedError, SecurityError
from ws_auth import Auth, WebsocketAuthProtocol

from .api import BaseController, ChannelResponse
from .exceptions import ChannelClosed, ReconnectTimeout, SHUTDOWN


class Channel:

    """Pass"""

    def __init__(
        self,
        resource: BaseController,
        *,
        auth: Auth = None,
        reconnect: bool = False,
        open_timeout: float = 10,
        dead_channel_timeout: float = 3600,
        loop: asyncio.AbstractEventLoop = None,
        **kwargs: Any
    ) -> None:

        self.url = resource.build_request().url
        self._reconnect = reconnect
        self._open_timeout = open_timeout
        self._dead_channel_timeout = dead_channel_timeout
        self._loop = loop or asyncio.get_event_loop()

        kwargs.update(
            {
                "auth": auth,
                "open_timeout": open_timeout
            }
        )
        self._websockets_args = kwargs

        self._buffer = deque()
        self._channel_closed_waiter: asyncio.Future = None
        self._channel_open: asyncio.Event = asyncio.Event()
        self._close_channel_waiter: asyncio.Future = None
        self._data_transfer_task: asyncio.Task = None
        self._init_channel_waiter: asyncio.Future = None
        self._pop_message_waiter: asyncio.Future = None
        self._reconnect_attempts: int = 0
        self._run_channel_task: asyncio.Task = None
        self._watchdog_task: asyncio.Task = None

    async def recv(self) -> ChannelResponse:

        """
        Receive API response from buffer

        Raises:
            - ChannelClosed: Channel was closed by user or system
            - RuntimeError: .recv() was called from another coroutine OR
            user specified a data_queue to feed responses to when a message
            is received
        Returns:
            ChannelResponse
        """

        if self._pop_message_waiter is not None:
            raise RuntimeError(
                "cannot call recv while another coroutine "
                "is already waiting for the next message"
            )
        if self._channel_closed_waiter is None:
            raise ConnectionResetError("Channel is not open")

        while (len(self._buffer)) <= 0:
            try:
                await self._channel_open.wait()
            except asyncio.CancelledError:
                await self.close(
                    exc=ReconnectTimeout(
                    "Operation cancelled by user while trying to reconnect"
                    )
                )
            pop_message_waiter: asyncio.Future = self._loop.create_future()
            self._pop_message_waiter = pop_message_waiter
            try:
                # If asyncio.wait() is canceled, it doesn't cancel
                # pop_message_waiter or self.datat_transfer_task.
                await asyncio.wait(
                    [pop_message_waiter, self._data_transfer_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
            finally:
                self._pop_message_waiter = None

            if not pop_message_waiter.done():
                await self._ensure_open()

        return self._buffer.popleft()

    async def close(self, exc: BaseException = None):
        """
        Close channel and clear buffer

        Raises:
            - ChannelClosed: an exception during shutdown or another
            exception occurred during operation of the channel
        """
        try:
            await self._shutdown()
        except Exception as err:
            raise ChannelClosed("Error occurred during shutdown") from err
        finally:
            self._buffer.clear()
        if exc is not None:
            raise ChannelClosed("Channel closed due to exception") from exc

    async def _start(self):
        """
        Start websocket connection process to Channel endpoint

        Raises:
            run_channel_task.exception: Exception encountered
            during connection. See ._run()
            asyncio.CancelledError: Task cancelled trying to
            establish websocket connection
        """
        
        init_channel_waiter = self._loop.create_future()
        self._init_channel_waiter = init_channel_waiter
        run_channel_task = self._loop.create_task(self._run())
        
        try:
            await asyncio.wait(
                [init_channel_waiter, run_channel_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            if not init_channel_waiter.done():
                raise run_channel_task.exception()
            
            self._run_channel_task = run_channel_task
        except asyncio.CancelledError:
            run_channel_task.cancel()
            raise
        finally:
            self._init_channel_waiter = None

    async def _run(self) -> None:
        """
        Open and manage websocket connection as background task. Supports reconnect
        if desired

        Raises:
            SecurityError: Too many redirects or insecure redirect
            asyncio.CancelledError: Task cancelled
            ConnectionClosedError: Websocket connection closed unexpectedly
            Exception: Unhandled exception in websockets.connect or data transfer
            task. Task may be allowed to reconnect
        """

        while True:
            # create waiter for channel close
            close_channel_waiter = self._loop.create_future()
            self._close_channel_waiter = close_channel_waiter

            # see if we need to wait for a reconnect delay
            try:
                reconnect_delay = self._get_reconnect_delay()
                if reconnect_delay > 0:
                    delay_task = self._loop.create_task(asyncio.sleep(reconnect_delay))
                    await asyncio.wait(
                        [close_channel_waiter, delay_task],
                        return_when=asyncio.FIRST_COMPLETED
                    )
                if close_channel_waiter.done():
                    raise SHUTDOWN
            except SHUTDOWN:
                self._close_channel_waiter = None
                break
            
            # attempt to open websocket connection
            try:
                connect_task = self._loop.create_task(websockets.connect(self.url, **self._websockets_args))
                await asyncio.wait(
                    [close_channel_waiter, connect_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
                if close_channel_waiter.done():
                    connect_task.cancel()
                    raise SHUTDOWN
                protocol = connect_task.result()
                if self._init_channel_waiter is not None:
                    self._init_channel_waiter.set_result(None)
            except SHUTDOWN:
                self._close_channel_waiter = None
                break
            # too many redirects, insecure redirect, or task cancelled
            except (SecurityError, asyncio.CancelledError):
                self._close_channel_waiter = None
                raise
            # exception trying to connect, may try to reconnect
            except Exception:
                self._close_channel_waiter = None
                if self._init_channel_waiter is not None:
                    raise
                if self._reconnect:
                    continue
                raise
            
            # connection aquired, channel is open
            self._channel_open.set()
            self._reconnect_attempts = 0
            # start data transfer task
            data_transfer_task = self._loop.create_task(self._transfer_data(protocol))
            self._data_transfer_task = data_transfer_task

            try:
                await asyncio.wait(
                    [close_channel_waiter, data_transfer_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
                # break loop if .close() called
                if close_channel_waiter.done():
                    raise SHUTDOWN
                # if close_channel_waiter isn't done, transfer data
                # task should have an exception. If it doesnt that is
                # a bug
                raise data_transfer_task.exception()
            except SHUTDOWN:
                await protocol.close()
                with suppress(Exception):
                    await data_transfer_task
                break
            # task cancelled while connected
            except asyncio.CancelledError:
                await protocol.close()
                with suppress(Exception):
                    await data_transfer_task
                raise
            # websocket connection closed unexpectedly
            except ConnectionClosedError:
                if self._reconnect:
                    continue
                raise
            # unhandled exception in data transfer task
            except Exception:
                if not protocol.closed:
                    # if the protocol is open close it
                    if protocol.open:
                        await protocol.close()
                    # if it is neither open nor closed it
                    # is the closing sequence, wait for close
                    else:
                        await protocol.wait_closed()
                if self._reconnect:
                    continue
                raise
            finally:
                self._close_channel_waiter = None
                self._data_transfer_task = None
                self._channel_open.clear()

    BACKOFF_MIN = 1.92
    BACKOFF_MAX = 60.0
    BACKOFF_FACTOR = 1.618
    BACKOFF_INITIAL = 5

    def _get_reconnect_delay(self):
        """
        Get reconnect delay for next connection attempt. Retries with
        exponential backoff capping at 60 seconds

        Returns:
            delay (float): time to wait to next connection attempt
        """
        if self._reconnect_attempts == 0:
            delay = random.random() * self.BACKOFF_INITIAL
        else:
            delay = self.BACKOFF_MIN * self._reconnect_attempts^2 * self.BACKOFF_FACTOR
            delay = min(delay, self.BACKOFF_MAX)
        self._reconnect_attempts += 1
        return delay

    async def _transfer_data(self, protocol: WebsocketAuthProtocol) -> None:
        """
        Continuously receive messages from a protocol instance. Received messages
        are converted to ChannelResponse instances and placed in an internal
        buffer

        Args:
            protocol (WebsocketAuthProtocol): Websocket protocol object
        """
        async for message in protocol:
            response = self._process_message(message)
            self._buffer.append(response)
            # wake up receiver if waiting for a message
            if self._pop_message_waiter is not None:
                self._pop_message_waiter.set_result(None)
                self._pop_message_waiter = None

    def _process_message(self, message: Union[bytes, str]) -> ChannelResponse:
        """
        Parse message from websocket to ChannelResponse object

        Args:
            message (Union[str, bytes]): Raw message returned from websocket

        Returns:
            ChannelResponse: Formatted PI Web API response
        """
        
        try:
            content = orjson.loads(message) if isinstance(message, bytes) else json.loads(message)
        except (json.JSONDecodeError, orjson.JSONDecodeError):
            message = message.decode() if isinstance(message, bytes) else message
            content = {
                "Errors": "Unable to parse response content",
                "ResponseContent": message
            }    
        return ChannelResponse(
            url=self.url,
            **content
        )

    async def _shutdown(self):
        if self._close_channel_waiter is not None:
            self._close_channel_waiter.set_result(None)
        if self._run_channel_task is not None:
            await asyncio.shield(self._run_channel_task)
                


