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


class MaxConnectionsReached(WebsocketClientError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)