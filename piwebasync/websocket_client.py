import functools
from typing import Any, Callable, Optional, Sequence

import websockets
import ws_auth
from websockets.datastructures import HeadersLike
from websockets.extensions import ClientExtensionFactory
from websockets.legacy.client import Connect
from websockets.typing import LoggerLike, Origin, Subprotocol
from ws_auth import Auth

from .api.models import APIRequest, APIResponse
from .api.controllers.base import BaseController


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

    def __init__(
        self,
        scheme: str = None,
        host: str = None,
        port: int = None,
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
        **kwargs: Any,
    ) -> None:

        self.scheme = scheme
        self.host = host
        self.port = port
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
    
    @classmethod
    async def connect(
        cls,
        controller: BaseController,
    ):
        pass