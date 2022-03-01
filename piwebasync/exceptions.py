class PIWebAsyncException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class APIException(PIWebAsyncException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class SerializationError(APIException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class HTTPClientError(PIWebAsyncException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class WebsocketClientError(PIWebAsyncException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ChannelClosed(WebsocketClientError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ChannelClosedError(ChannelClosed):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ChannelClosedOK(ChannelClosed):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ChannelUpdateError(WebsocketClientError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class WatchdogTimeout(WebsocketClientError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
