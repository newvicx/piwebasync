from datetime import datetime
from typing import(
    ByteString,
    Dict,
    List,
    Protocol,
    Tuple,
    Union
)


class APIRequestType(Protocol):
    @property
    def absolute_url(self):
        ...


class ControllerType(Protocol):
    def _build_request(self, *args, **kwargs):
        ...


class StrCompatible(Protocol):
    def __str__(self):
        ...


JSONPrimitive = Union[
    str,
    float,
    datetime,
    bool,
    int,
]

JSONType = Union[
    "JSONType",
    JSONPrimitive,
    Dict[str, "JSONType"],
    List["JSONType"]
]

ConvertsToStr = Union[
    "ConvertsToStr",
    ByteString,
    datetime,
    float,
    int,
    List["ConvertsToStr"],
    Tuple["ConvertsToStr"],
]

StrType = Union[
    str,
    ConvertsToStr
]

QueryStrType = str
