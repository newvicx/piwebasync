from typing import Any, Dict, List, Union

import orjson
from httpx import Headers
from pydantic import BaseModel, root_validator, validator

from ...exceptions import HttpStatusError, PiWebException
from .._serialization import deserialize_camel_case



JSON = Union[str, int, float, bool, None, Dict[str, "JSON"], List["JSON"]]


class Empty:

    def __getattribute__(self, __name: str) -> "Empty":
        return Empty()
    
    def __bool__(self):
        return False
    
    def __iter__(self):
        return self
    
    def __next__(self):
        raise StopIteration

    def get(self, __name: str, __default: Any) -> "Empty":
        return Empty()

    def __getitem__(self, __name: str) -> "Empty":
        return Empty()


class BaseContent(BaseModel):
    """
    Base class for Pi Web API content. Ensures all top level
    attributes are snake case attributes
    """
    class Config:
        extra = "allow"

    @root_validator(pre=True)
    def _normalize_keys(cls, values: Dict[str, JSON]) -> Dict[str, JSON]:
        normalized = {
            deserialize_camel_case(key): val for key, val in values.items()
        }
        return normalized

    def __getattribute__(self, __name: str) -> Any:
        try:
            return super().__getattribute__(__name)
        except AttributeError:
            return Empty()


class WebException(BaseContent):
    """
    WebException attribute model for PI Web API response

    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/topics/error-handling.html
    """
    errors: List[str]
    status_code: int

    class Config:
        extra = "forbid"

    def raise_err(self):
        if 200 <= self.status_code <= 299:
            raise PiWebException(
                "PI Web API encountered an unhandled error "
                "during the transfer of the response stream"
            ) from HttpStatusError(
                status_code=self.status_code,
                errors=self.errors
            )


class Links(BaseContent):
    """
    Links attribute model for PI Web API response
    """


class PiWebContent(BaseContent):
    """
    Primary implementation for JSON content returned
    from the Pi Web API. It can accept any controller
    respone content

    Should not be used for for stream and streamset
    controllers which return a lot of data as it
    can be comparatively slow
    """
    class Config:
        extra = "allow"
        json_loads = orjson.loads

    @root_validator(skip_on_failure=True)
    def _interpolate_schema(cls, values: Dict[str, JSON]):
        """
        Recursively construct sub content objects from dicts
        contained in the main response body
        """
        interpolated = values.copy()
        for key, val in values.items():
            if key == "links":
                interpolated[key] = Links(**val)
            elif key == "web_exception":
                interpolated[key] = WebException(**val)
            elif isinstance(val, dict):
                interpolated[key] = PiWebContent(**val)
            elif isinstance(val, list):
                interpolated[key] = [
                    PiWebContent(**item) if isinstance(item, dict) else item
                    for item in val
                ]
        return interpolated

    def raise_for_web_exception(self):
        """
        Check for and raise any WebException errors
        """
        web_exception = self.web_exception
        if web_exception is not None:
            web_exception.raise_err()


class HttpResponse(BaseModel):
    status_code: int
    headers: Headers
    content: PiWebContent

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True

    @validator('headers')
    def _validate_headers(cls, headers: Headers) -> Headers:
        """
        Validate header attribute type
        """
        assert isinstance(headers, Headers), (
            f"Headers must be type 'httpx.Headers', got {type(headers)}"
        )

    def raise_for_status(self):
        """
        Check for and raise HttpStatusError
        """
        if 200 <= self.status_code <= 299:
            raise HttpStatusError(
                status_code=self.status_code,
                errors=self.content._errors
            )
        self.content.raise_for_web_exception()