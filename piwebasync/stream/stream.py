import asyncio
import logging
import uuid
from types import TracebackType
from typing import Any, Callable, Type

from piwebasync import APIRequest, APIResponse, WebsocketClient
from piwebasync.exceptions import ChannelClosedError


class Stream:

    """
    Self managed stream processor for PI Web API
    
    Each stream represents a single websocket connection to
    the PI Web API. Data is received, processed, and placed in a queue.

    ```python
    stream = Stream(queue)
    stream_id = await stream.start(request, handler)
    await stream.stop()
    ```
    
    **Parameters**
    - **queue** (*asyncio.Queue*): a queue to insert processed messages
    - **auth** (*ws_auth.Auth*): the authorization flow to connect to the
    PI Web API
    - **dead_channel_timeout** (*float*): time in seconds the WebsocketClient
    will attempt to reconnect before failing the connection
    - **logger** (*logging.Logger*): logger for class
    - **loop** (*asyncio.AbstractEventLoop*): event loop
    """

    def __init__(
        self,
        client: WebsocketClient,
        queue: asyncio.Queue,
        parser: Callable[[APIResponse], Any],
        logger: logging.Logger = None,
        loop: asyncio.AbstractEventLoop = None
    ):

        self._client = client
        self._queue = queue
        self._parser = parser
        self._logger = logger or logging.getLogger(__name__)
        self._loop = loop or asyncio.get_event_loop()

        _id = uuid.uuid4().hex
        self._channel: WebsocketClient = None
        self._id = _id
        
        self._close_stream_task: asyncio.Task = None
        self._close_stream_waiter: asyncio.Future = None
        self._data_processing_event: asyncio.Event = asyncio.Event()
        self._run_stream_task: asyncio.Task = None
        self._state_lock: asyncio.Lock = asyncio.Lock()
        self._stream_error_callback: asyncio.Future = None

    @property
    def is_running(self):
        """
        `True` when stream processor is running and can process data.
        `False` otherwise
        """
        return self._data_processing_event.is_set()

    @property
    def is_closed(self):
        """
        `True` when `stop()` has been called or stream was never started.
        `False` otherwise 
        """
        return self._close_stream_task is None

    @property
    def client(self):
        return self._client

    async def start(
        self,
        on_error_callback: Callable[[asyncio.Future], None] = None
    ) -> str:
        """
        Start stream processor

        Opens a websocket connection to the PI Web API and starts
        a processing task in the background.

        **Parameters**
        - **request** (*APIRequest*): the websocket endpoint to connect to
        - **handler** (*Callable[[APIResponse], Any]*): parser for
        new messages. Raw messages always pass through the handler before
        being put into the queue

        **Returns**
        - **_id** (*str*): the unique id assigned to the stream

        **Raises**
        - **asyncio.TimeoutError**: Timed out trying to open websocket
        - **TypeError**: request is not an instance of APIRequest
        - **ValueError**: WebsocketClient does not support this request
        - **RuntimeError**: Stream is running
        """

        async with self._state_lock:
            if self.is_running:
                raise RuntimeError("Stream is running")
            run_stream_task = self._loop.create_task(self._run())
            self._run_stream_task = run_stream_task
            stream_error_callback = self._loop.create_future()
            if on_error_callback is not None:
                stream_error_callback.add_done_callback(on_error_callback)
            self._stream_error_callback = stream_error_callback
            # ensure data processing starts before creating closing task
            await self._data_processing_event.wait()
            close_stream_task = self._loop.create_task(self._close())
            self._close_stream_task = close_stream_task

    async def stop(self) -> None:
        """
        Stop the stream processor

        `stop()` is idempotent, subsequent calls to `stop()` will have
        no effect. Any errors which caused the stream processor to stop
        prematurely will be raised in the first call to `stop()`

        **Raises**
        - **ChannelClosedError**: the WebsocketClient closed prematurely
        - **WatchdogTimeout**: the WebsocketClient closed due to timing
        out trying to reconnect
        - **ChannelUpdateError**: the WebsocketClient closed due to an error
        trying to update the endpoint
        """
        async with self._state_lock:
            if self.is_closed:
                return
            try:
                if self._close_stream_waiter is not None:
                    self._close_stream_waiter.set_result(None)
                await self._close_stream_task
            finally:
                self._close_stream_task = None


    async def update(self, request: APIRequest, rollback: bool = True):
        """
        Update the PI Web API endpoint of the stream processor
        without stopping it

        **Raises**
        - **ChannelUpdateError**: Unable to establish a connection
        to the new endpoint (will cause stream to stop)
        - **TypeError**: request is not an instance of APIRequest
        (this will not cause the stream to stop)
        - **ValueError**: WebsocketClient does not support this request
        (this will not cause the stream to stop)
        - **RuntimeError**: the stream is not running
        """
        if not self.is_running:
            raise RuntimeError("Stream is not running")

        async with self._state_lock:
            await self.client.update(request, rollback=rollback)

    async def _run(self):
        """
        Run data processing
        
        Receives message from websocket connection, processes them and
        puts them into a queue
        """
        async with self._client as channel:
            try:
                self._data_processing_event.set()
                async for message in channel:
                    try:
                        data = self._handler(message)
                    except Exception:
                        self._logger.error(
                            "Error processing message %s",
                            message.raw_response,
                            exc_info=True
                        )
                        continue
                    await self._queue.put(data)
            except ChannelClosedError as err:
                self._logger.error(
                    "Error occurred during stream processing",
                    exc_info=True
                )
                raise err
            except asyncio.CancelledError:
                return
            finally:
                self._data_processing_event.clear()

    async def _close(self):
        """
        Ensure stream processor closes properly
        
        Started as task once the stream is confirmed to be running
        """
        close_stream_waiter = self._loop.create_future()
        self._close_stream_waiter = close_stream_waiter
        try:
            await asyncio.wait(
                [close_stream_waiter, self._run_stream_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            if not close_stream_waiter.done():
                self._logger.debug("Executing run_stream_task callback")
                self._stream_error_callback.set_exception(self._run_stream_task.exception())
        except asyncio.CancelledError:
            pass
        finally:
            self._close_stream_waiter = None
            self._stream_error_callback = None
        if not self._run_stream_task.done():
            self._run_stream_task.cancel()
        try:
            await asyncio.shield(self._run_stream_task)
        finally:
            self._run_stream_task = None

    async def __aenter__(self) -> "Stream":
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        await self.stop()