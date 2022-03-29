from typing import Any, Dict, List, Optional, Union

import orjson
from httpx import Headers
from httpx._status_codes import codes
from piwebasync.api.controllers.dataservers import DataServers
from piwebasync.api.controllers.eventframes import EventFrames
from pydantic import(
    BaseModel,
    ValidationError,
    root_validator,
    validator
)

from .controllers import(
    AssetDatabases,
    AssetServers,
    Attributes,
    DataServers,
    Elements,
    EventFrames,
    Points,
    Streams,
    StreamSets,
)
from ..exceptions import HTTPStatusError
from ..types import JSONType
from .util import(
    json_dump_content,
    json_load_content,
    normalize_camel_case,
    normalize_request_params,
    normalize_response_key,
    search_response_content,
    serialize_multi_instance,
    serialize_semi_colon_separated,
)


class Controller:
    """
    Base class for all PI Web API controllers. Provides a standardized
    API for constructing APIRequests. All supported PI Web API controllers
    can be accessed as attributes of the base Controller instance

    **Usage**

    ```python
    # Chaining
    request: APIRequest = Controller(scheme, host, port, root).streams.get_end(webid)

    # Reuse base URL
    controller: Controller = Controller(scheme, host, port, root)
    request_1: APIRequest = controller.streams.get_end(webid)
    request_2: APIRequest = controller.streams.get_recorded(webid)
    ```

    **Parameters**

    - **scheme** (*str*): URL scheme; *"http"*, *"https"*, *"ws"*, *"wss"*
    - **host** (*str*): PI Web API host address
    - **port** (*Optional(str)*): the port to connect to
    - **root** (*Optional(str)*): root path to PI Web API
    """
    
    SEMI_COLON_PARAMS = [
        "selected_fields",
        "annotations"
    ]
    MULTI_INSTANCE_PARAMS = {
        "web_id": "webId",
        "times": "time",
        "paths": "path",
        "security_item_many": "securityItem",
        "user_identity_many": "userIdentity",
        "severity_many": "severity",
        "trait_many": "trait",
        "trait_category_many": "trait_category",
    }

    def __init__(
        self,
        scheme: str,
        host: str,
        port: int = None,
        root: str = "/"
    ) -> None:

        self.scheme = scheme
        self.host = host
        self.port = port
        self.root = root

    @property
    def assetdatabases(self) -> AssetDatabases:
        return AssetDatabases(self)

    @property
    def assetservers(self) -> AssetServers:
        return AssetServers(self)

    @property
    def attributes(self) -> Attributes:
        return Attributes(self)

    @property
    def dataservers(self) -> DataServers:
        return DataServers(self)

    @property
    def elements(self) -> Elements:
        return Elements(self)

    @property
    def eventframes(self) -> EventFrames:
        return EventFrames(self)

    @property
    def points(self) -> Points:
        return Points(self)

    @property
    def streams(self) -> Streams:
        return Streams(self)

    @property
    def streamsets(self) -> StreamSets:
        return StreamSets(self)

    def _build_request(
        self,
        method: str,
        protocol: str,
        controller: str,
        action: str = None,
        webid: str = None,
        add_path: List[str] = None,
        **params: Any
    ):
        """Serialize params and return APIRequest instance"""
        serialized_params = self._serialize_params(params)
        return APIRequest(
            root=self.root,
            method=method,
            protocol=protocol,
            controller=controller,
            scheme=self.scheme,
            host=self.host,
            port=self.port,
            action=action,
            webid=webid,
            add_path=add_path,
            **serialized_params
        )
    
    def _serialize_params(self, params: Dict[str, Any]):
        """Serialize semi colon and multi instance params to URL safe strings"""
        # serialize semi colon params
        for validate in self.SEMI_COLON_PARAMS:
            param = params.get(validate)
            if param is not None:
                serialized = serialize_semi_colon_separated(param)
                params.update({validate: serialized})
        # validate multi instance params
        for validate, key in self.MULTI_INSTANCE_PARAMS.items():
            param = params.get(validate)
            if param is not None:
                serialized = serialize_multi_instance(key, param)
                params.pop(validate)
                params.update({key: serialized})
        return params


class APIRequest(BaseModel):
    """
    Base model for Pi Web API requests. An API request is passed to a
    client instance to handle the request. You will not typically create
    APIRequest objects yourself. Generally, you should use the *Controller*
    object instead. However, for non supported controllers and controller
    methods you may want to create your own APIRequest directly

    **Parameters**

    - **root** (*str*): root path to PI Web API
    - **method** (*str*): the HTTP method for the request
    - **protocol** (*str*): request protocol to use; either *"HTTP"* or *"Websockets"*
    - **controller** (*str*): the controller being accessed on the PI Web API
    - **scheme** (*str*): URL scheme; *"http"*, *"https"*, *"ws"*, *"wss"*
    - **host** (*str*): PI Web API host address
    - **port** (*Optional(str)*): the port to connect to
    - **action** (*Optional(str)*): the PI Web API controller method, this is a path parameter
    - **webid** (*Optional(str)*): the WebId of a resource, this is a path parameter
    - **add_path** (*Optional(list[str])*): additional path parameters to be included.
    > List elements are added to the end of the path in order separated by a "/"
    - **kwargs** (*Optional(Any)*): query parameters for controller method
    """
    root: str
    method: str
    protocol: str
    controller: str
    scheme: str
    host: str
    port: Optional[int]
    action: Optional[str]
    webid: Optional[str]
    add_path: Optional[List[str]]
    
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
    """
    Base model for PI Web API responses. Users will never create APIResponse
    objects directly. Instead, *HTTPResponse* and *WebsocketMessage*
    instances will be returned from the *HTTPClient* and *WebsocketClient*
    respectively. The APIResponse model handles errors in the body of a
    response and normalizes all arguments from camel case to snake case

    **Parameters**

    - **kwargs** (*Optional(Any)*): Any content to be included in response
    """

    class Config:
        extra="allow"
        arbitrary_types_allowed=True
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
    def normalize_response(cls, values: Dict[str, JSONType]) -> Dict[str, JSONType]:
        """
        Normalize top level keys from response body to snake case
        """
        return {normalize_response_key(key): val for key, val in values.items()}

    @property
    def raw_response(self) -> bytes:
        """
        Reproduce raw response body from PI Web API as bytes
        """
        response = self.dict()
        return orjson.dumps(response)

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Restore camel case for top level response content
        """
        response = super().dict(*args, **kwargs)
        return {normalize_camel_case(key): val for key, val in response.items()}
    
    def select(self, *fields: str) -> Dict[str, JSONType]:
        """
        Returns the values of the selected fields from the response content.
        'fields' are defined using dot notation (Top.Nested.NestedNested)
        """
        response = self.dict()
        return {field: search_response_content(field, response) for field in fields}


class HTTPResponse(APIResponse):
    status_code: int
    url: str
    headers: Headers

    class Config:
        extra="allow"
        arbitrary_types_allowed=True
        fields = {
            "status_code": {"exclude": True},
            "url": {"exclude": True},
            "headers": {"exclude": True},
        }
        json_loads=json_load_content
        json_dumps=json_dump_content

    def raise_for_status(self):
        """
        Raise HTTPStatusErorr for non successful request or error
        parsing content
        """
        
        status_code = self.status_code
        if not codes.is_success(status_code):
            reason_phrase = codes.get_reason_phrase(status_code)
            errors = self.dict().get('Errors')
            message = f"{status_code}: {reason_phrase}. The following errors occurred {errors}"
            raise HTTPStatusError(message)
        elif codes.is_success(status_code) and self.dict().get('ErrorMessage') is not None:
            reason_phrase = "JSON Parsing Error"
            errors = self.dict().get('ErrorMessage')
            message = f"{status_code}: {reason_phrase}. The following errors occurred {errors}"
            raise HTTPStatusError(message)

class WebsocketMessage(APIResponse):
    url: str

    class Config:
        extra="allow"
        arbitrary_types_allowed=True
        fields = {
            "url": {"exclude": True},
        }
        json_loads=json_load_content
        json_dumps=json_dump_content