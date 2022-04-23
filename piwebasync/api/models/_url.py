from enum import Enum
from typing import Dict, Optional, Sequence, Union
from urllib.parse import unquote

from pydantic import (
    AnyUrl,
    BaseModel,
    validator
)
from yarl import URL

from ._query import AbstractQueryParam
from ._response import BaseContent, PiWebContent



class PiWebHttpMethods(str, Enum):
    delete = "DELETE"
    get = "GET"
    patch = "PATCH"
    post = "POST"
    put = "PUT"


class PiWebUrl(BaseModel):
    """
    Base constructor for a PI Web API URL

    The URL structure is...
    [scheme:]//[host][:port][/path][?query]
    
    A few notes...
    - PI Web API URL's do not contain fragments
    - PI Web API URL's do not contain user information

    The path of the URL is further broken down...
    [/root][/controller][/webid_path][/action][/add_path]
    \_____/\___________/\_______________________________/
    Part     Required               Optional
    of
    base_url

    **Parameters**
    - **base_url** (*AnyUrl*): The base URL including, at a
    minumum, scheme and host. Must not contain any user info,
    query parameters or fragments
    - **controller** (*str*): The PI Web API controller
    - **webid_path** (*Optional[str]*): The WebId of the
    resource. Used as a path parameter
    - **action** (*Optional[str]*): The action of the controller
    - **add_path** (*Optional[Sequence[str]]*): Any additional path
    parameters to add to the URL. Added in order as they appear
    in the sequence
    - **query** (*Optional[Sequence[AbstractQueryParam]]*): Sequence
    of query parameters for URL
    """
    base_url: AnyUrl
    controller: str
    webid_path: Optional[str]
    action: Optional[str]
    add_path: Optional[Sequence[str]] = []
    query_params: Optional[
        Union[
            str,
            Dict[str, Union[str, int, float]],
            Sequence[AbstractQueryParam]
        ]
    ]
    response_model: Optional[BaseContent] = PiWebContent

    @validator('base_url')
    def _validate_base_url(cls, base_url: AnyUrl) -> AnyUrl:
        """
        Assert base URL does not contain user information, query parameters
        or fragments
        """
        assert not base_url.user and not base_url.password, "Base URL contains user/password"
        assert not base_url.query, "Base URL contains query"
        assert not base_url.fragment, "Base URL contains fragment"
        return base_url
    
    @validator('base_url')
    def _normalize_base_path(cls, base_url: AnyUrl) -> URL:
        """
        Ensure base path always ends with '/'
        """
        base_path = '/'
        path = base_url.path
        if path:
            split_delim = path.split('/')
            path_params = [component for component in split_delim if component]
            base_path += '/'.join(path_params)
            base_path += '/'
        return URL.build(
            scheme=base_url.scheme,
            host=base_url.host,
            port=base_url.port,
            path=base_path
        )

    @property
    def url(self) -> str:
        """
        Derive absolute URL
        """
        query = self.query
        path = self.path
        relative_url = URL.build(path=path, query=query)
        absolute_url = self.base_url.join(relative_url)
        return unquote(str(absolute_url), encoding='ascii')

    @property
    def path(self) -> str:
        """
        Derive full path of URL
        """
        path_params = [
            self.controller,
            self.webid_path,
            self.action,
            *self.add_path
        ]
        while True:
            try:
                path_params.remove(None)
            except ValueError:
                break
        request_path = '/'.join(path_params)
        return self.base_url.path + request_path

    @property
    def query(self) -> Union[str, Dict[str, Union[str, int, float]]]:
        """
        Return serialized query params
        """
        if isinstance(self.query_params, (str, dict)):
            return self.query_params
        query = {}
        for param in self.query_params:
            field_name, value = param.serialized
            query[field_name] = value
        return query


class PiWebHttpUrl(PiWebUrl):
    """
    HTTP URL constructor for a Pi Web API URL
    """
    http_method: PiWebHttpMethods
    
    @validator('base_url')
    def _validate_scheme(cls, base_url: AnyUrl) -> AnyUrl:
        assert base_url.scheme.lower() in ['http', 'https'], f"Invalid scheme '{base_url.scheme}'"
        return base_url


class PiWebWebsocketUrl(PiWebUrl):
    """
    Websocket URL constructor for a Pi Web API URL
    """
    @validator('base_url')
    def _validate_scheme(cls, base_url: AnyUrl) -> AnyUrl:
        assert base_url.scheme.lower() in ['ws', 'wss'], f"Invalid scheme '{base_url.scheme}'"
        return base_url