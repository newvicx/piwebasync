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


class SHUTDOWN(WebsocketClientError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ReconnectTimeout(WebsocketClientError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)