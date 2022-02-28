class PIWebAPIException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class SerializationError(PIWebAPIException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class HTTPClientError(PIWebAPIException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class WebsocketClientError(PIWebAPIException):
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
