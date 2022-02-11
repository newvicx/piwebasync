from typing import Dict, List, Optional, Union

import orjson
from httpx import Headers, URL
from pydantic import BaseModel, ValidationError, root_validator, validator

from ..httpx_util.models import SafeURL
from ..types import JSONType
from ..util import(
    json_dump_content,
    json_load_content,
    normalize_camel_case,
    normalize_request_params,
    normalize_response_key,
    search_response_content,
)


class APIRequest(BaseModel):
    """Base model for Pi Web API requests"""
    method: str
    root: str
    protocol: str
    controller: Optional[str]
    webid: Optional[str]
    action: Optional[str]
    add_path: Optional[List[str]]
    scheme: Optional[str]
    host: Optional[str]
    port: Optional[int]
    
    class Config:
        extra="allow"
        arbitrary_types_allowed=True
        fields={
            "method": {"exclude": True},
            "root": {"exclude": True},
            "protocol": {"exclude": True},
            "controller": {"exclude": True},
            "webid": {"exclude": True},
            "action": {"exclude": True},
            "add_path": {"exclude": True},
            "scheme": {"exclude": True},
            "host": {"exclude": True},
            "port": {"exclude": True}
        }
        json_dumps=json_dump_content

    @validator("method")
    def validate_method(cls, method: str) -> str:
        """Check method is valid value"""
        valid_methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
        if method not in valid_methods:
            raise ValidationError(f"Request method must be one of valid methods, {valid_methods}")
        return method
    
    @validator("protocol")
    def validate_protcol(cls, protocol: str) -> str:
        """Check protocol is valid value"""
        valid_protocols = ["HTTP", "Websocket"]
        if protocol not in valid_protocols:
            raise ValidationError(f"Protocol must be one of valid protocols, {valid_protocols}")
        return protocol
    
    @validator("root")
    def normalize_root(cls, root: str) -> str:
        """Add leading and trailing slash to root"""
        try:
            if root[0] != "/":
                root = '/' + root
            if root[-1] != "/":
                root = root + '/'
        except IndexError:
            root = '/'
        return root
    
    @validator("add_path")
    def validate_add_path(cls, add_path: Union[None, list]) -> str:
        """Converts add_path from None to [] if applicable"""
        if add_path is None:
            return []
        return add_path

    @property
    def absolute_url(self) -> str:
        if not self.host or not self.scheme:
            raise ValueError(
                "Cannot build absolute url without host and scheme"
            )
        port = self.port
        if port:
            return f"{self.scheme}://{self.host}:{port}" + self.raw_path
        return f"{self.scheme}://{self.host}" + self.raw_path
    
    @property
    def params(self) -> Dict[str, str]:
        """Get normalized query params as dict"""
        raw_params = self.dict()
        return normalize_request_params(raw_params)
    
    @property
    def path(self) -> str:
        """Return URL path"""
        add_path = '/'.join(self.add_path) or None
        path_params = [self.controller, self.webid, self.action, add_path]
        while True:
            try:
                path_params.remove(None)
            except ValueError:
                break
        return f"{self.root}" + "/".join(path_params)
    
    @property
    def query(self) -> str:
        """Get normalized query params as str"""
        params = self.params
        joined = [f"{key}={param}" for key, param in params.items() if param is not None]
        return "&".join(joined)
    
    @property
    def raw_path(self) -> str:
        """Get url target"""
        query = self.query
        if query:
            return f"{self.path}" + f"?{query}"
        return self.path


class APIResponse(BaseModel):
    """Base model for Pi Web API responses"""
    status_code: int
    url: Union[URL, SafeURL]
    headers: Headers
    normalize: bool = False

    class Config:
        extra="allow"
        arbitrary_types_allowed=True
        fields = {
            "status_code": {"exclude": True},
            "url": {"exclude": True},
            "normalize": {"exclude": True},
        }
        json_loads=json_load_content
        json_dumps=json_dump_content
    
    @root_validator(pre=True)
    def handle_web_exception(cls, values: Dict[str, JSONType]) -> Dict[str, JSONType]:
        """
        Handles WebException property in response body (if present).
        See link for error handling and WebException property
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/topics/error-handling.html
        """
        # handle WebException property, update status_code and errors fields
        web_exception = values.get('WebException')
        if web_exception is not None:
            errors = values.get('Errors')
            if not errors:
                errors = web_exception["Errors"]
            else:
                errors.extend(web_exception["Errors"])
            status_code = web_exception['StatusCode']
            values.update(
                {
                    'Errors': errors,
                    'status_code': status_code
                }
            )
        return values
    
    @root_validator
    def normalize(cls, values: Dict[str, JSONType]) -> Dict[str, JSONType]:
        """Normalize keys from response body to snake case"""
        should_normalize = values.get("normalize")
        if should_normalize:
            return {normalize_response_key(key): val for key, val in values.items()}
        return values

    @property
    def raw_response(self) -> bytes:
        """Reproduce raw response content as bytes. Raw response is valid JSON to deserialize"""
        response = self.dict()
        if self.normalize:
            response = {normalize_camel_case(key): val for key, val in response.items()}
        return orjson.dumps(response)
    
    def select(self, *fields: str) -> Dict[str, JSONType]:
        """
        Returns with the values of the selected fields from the response content.
        Define 'fields' using dot notation (Top.Nested.NestedNested)
        """
        response = self.dict()
        if self.normalize:
            response = {normalize_camel_case(key): val for key, val in response.items()}
        return {field: search_response_content(field, response) for field in fields}
    
    def to_polars(self, *args, **kwargs):
        """
        Convert response into a polars dataframe. Implemented by controller
        response objects based on the expected schema
        """
        raise NotImplementedError()
    
    def to_pandas(self, *args, **kwargs):
        """
        Convert response to pandas dataframe. Implemented by controller
        response objects based on the expected schema
        """
        raise NotImplementedError()
