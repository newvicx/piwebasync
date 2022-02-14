import asyncio
import functools
import json
import uuid
from collections import deque
from typing import Any, Callable, Optional, Sequence

import orjson
import websockets
from websockets.datastructures import HeadersLike
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
from websockets.extensions import ClientExtensionFactory
from websockets.typing import LoggerLike, Origin, Subprotocol
from ws_auth import Auth, WebsocketAuthProtocol

from .api.models import APIRequest, APIResponse
from .api.controllers.base import BaseController
from .exceptions import BufferConsumed, MaxConnectionsReached


class PIChannel:
    
    """PI Web API Channel connection"""

    def __init__(
        self,
        url: str,
        client: WebsocketClient,
        connection_factory: dict,
        reconnect: bool = False,
        loop: asyncio.AbstractEventLoop = None,
    ) -> None:
        
        self.url = url
        self.client = client
        self.connection_factory_kwargs = connection_factory.pop("kwargs", {})
        self.connection_factory = connection_factory
        self.reconnect = reconnect
        self.loop = loop or asyncio.get_event_loop()

        self._id = uuid.uuid4().hex
        self._close_channel = asyncio.Event()
        self._channel_open = asyncio.Event()
        self._channel_closed_waiter = None
        self._channel_close_exc = None
        self._channel_connect_task = None
        self._pop_message_waiter = None

    async def start(self) -> None:
        pass

    async def recv(self) -> APIResponse:
        pass

    async def update(self, url: str) -> None:
        pass

    async def close(self) -> None:
        pass
    
    def _process_message(self, message: Union[str, bytes]) -> APIResponse:
        try:
            content = json.loads(message) if isinstance(message, str) else orjson.loads(message)
        except json.JSONDecodeError:
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

    async def _connect_channel(self) -> None:
        async for connection in websockets.connect(
            self.url,
            **self.ws_connect_params,
            **self.ws_connect_kwargs
        ):
            self._channel_open.set()
            self.connection = connection
            try:
                async for message in connection:
                    response = self._process_message(message)
                    self.buffer.append(response)
                    if self._pop_message_waiter is not None:
                        self._pop_message_waiter.set_result(None)
                        self._pop_message_waiter = None
            except ConnectionClosedOK:
                if self._close_channel.is_set() or not self.reconnect:
                    break
                logger.info("Reconnecting to %s", self.url)
                continue
            except ConnectionClosedError as err:
                logger.warning("Channel connection closed unexpectedly: %r", err)
                if self._close_channel.is_set() or not self.reconnect:
                    raise err
                logger.info("Reconnecting to %s", self.url)
                continue
            except asyncio.CancelledError as err:
                await connection.close
                raise err
            except Exception as err:
                logger.warning("Unhandled exception in channel: %r", err)
                await connection.close()
                raise err
            finally:
                self._channel_open.clear()
                self.connection = None

    async def _shutdown(self) -> None:
        self._close_channel.set()
        if self.connection is not None:
            await self.connection.close()
        if not self._channel_connect_task.done():
            self._channel_connect_task.cancel()



    async def __aiter__(self) -> AsyncIterator[APIResponse]:
        pass
