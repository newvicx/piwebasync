from functools import wraps
from inspect import signature
from typing import Any, Callable, Dict, List, Sequence

from pydantic import AnyUrl, BaseModel, Field, create_model

from ._query import AbstractQueryParam, QueryParam
from ._response import BaseContent, PiWebContent
from ._url import PiWebHttpUrl, PiWebWebsocketUrl


class BaseController(BaseModel):
    """
    Base controller model for all Pi Web API endpoint
    definitions

    Endpoints should dynamically create a model with
    its base as this class. The model can then have
    the query parameters casted and validated then
    converted to the appropriate URL depending on the
    controller method used
    """
    base_url: AnyUrl = Field(..., exclude=True)
    controller: str = Field(..., exclude=True)

    def cast_query_params(
        self,
        **kwargs: Dict[str, AbstractQueryParam]
    ) -> List[AbstractQueryParam]:
        """
        Cast the requested field names to the query param
        model provided. All other parameters will be casted
        to QueryParam
        """
        model_keys = list(self.dict().keys())
        cast_keys = list(kwargs.keys())
        invalid_keys = set(cast_keys) - set(model_keys)
        if invalid_keys:
            raise ValueError(
                "The following fields cannot be casted. "
                "Fields are not in controller request model: "
                f"{', '.join(invalid_keys)}"
            )
        fields = self.dict(exclude_none=True)
        query_params = []
        for field_name, value in fields.items():
            if field_name in cast_keys:
                model = kwargs[field_name]
                query_params.append(
                    model(
                        field_name=field_name,
                        value=value
                    )
                )
            else:
                query_params.append(
                    QueryParam(
                        field_name=field_name,
                        value=value
                    )
                )
        return query_params

    def http_url(
        self,
        http_method: str,
        *,
        webid_path: str = None,
        action: str = None,
        add_path: Sequence[str] = None,
        query_params: Sequence[AbstractQueryParam] = None
    ) -> PiWebHttpUrl:
        """
        Generate PiWebHttpUrl from controller model
        """
        params = {
            'http_method': http_method,
            'base_url': self.base_url,
            'controller': self.controller,
            'webid_path': webid_path,
            'action': action,
            'add_path': add_path,
            'query_params': query_params
        }
        model_config = {param: val for param, val in params.items() if val is not None}
        return PiWebHttpUrl(**model_config)

    def websocket_url(
        self,
        *,
        webid_path: str = None,
        action: str = None,
        add_path: Sequence[str] = None,
        query_params: Sequence[AbstractQueryParam] = None
    ) -> PiWebWebsocketUrl:
        """
        Generate PiWebWebsocketUrl from controller model
        """
        params = {
            'base_url': self.base_url,
            'controller': self.controller,
            'webid_path': webid_path,
            'action': action,
            'add_path': add_path,
            'query_params': query_params
        }
        model_config = {param: val for param, val in params.items() if val is not None}
        return PiWebWebsocketUrl(**model_config)


def generate_controller_model(
    self,
    controller_method: Callable[[Any], Any],
    args,
    kwargs,
    webid_path: str = None,
    action: str = None,
    add_path: Sequence[str] = None,
    cast: Dict[str, AbstractQueryParam] = {},
    map_to_url: Dict[str, str] = {},
    map_param_names: Dict[str, str] = {},
):
    """
    Dynamically create a controller model from function
    type hints
    """
    # the controller method doesn't return anything
    # this checks for any passed positional args
    controller_method(self, *args, **kwargs)
    # if one of the three url args below is also mapped,
    # the given value will be overwritten with the mapped
    # value
    url_args = {
        'webid_path': webid_path,
        'action': action,
        'add_path': add_path
    }
    mapped_url_args = {
        mapped_arg: kwargs.pop(key)
        for key, mapped_arg in map_to_url.items()
    }
    url_args.update(mapped_url_args)
    # PiWebUrl does not accept NoneType for any url params
    url_args = {
        key: val for key, val in url_args.items()
        if val is not None
    }
    params = signature(controller_method).parameters
    field_definitions = {}
    for name, param in params.items():
        if name == "self" or name in map_to_url:
            continue
        # required keyword parameters
        if param.default is param.empty:
            field_definitions[name] = (param.annotation, ...)
        # optional keyword parameters
        else:
            field_definitions[name] = (param.annotation, param.default)
    # map param names
    for key, mapped_name in map_param_names.items():
        try:
            field_definitions[mapped_name] = field_definitions.pop(key)
        except KeyError:
            pass
    # dynamically create pydantic model
    class_name = self.__class__.__name__
    method_name = controller_method.__name__
    slug = f"{class_name}_{method_name}"
    controller_model = create_model(
        slug,
        __base__=BaseController,
        **field_definitions
    )
    inst = controller_model(
        base_url=self._base_url,
        controller=self._controller,
        **kwargs
    )
    query_params = inst.cast_query_params(**cast)
    return inst, query_params, url_args


def http_request(
    http_method: str,
    webid_path: str = None,
    action: str = None,
    add_path: Sequence[str] = None,
    cast: Dict[str, AbstractQueryParam] = {},
    map_to_url: Dict[str, str] = {},
    map_param_names: Dict[str, str] = {},
    response_model: BaseContent = PiWebContent
):
    def http_request_decorator(controller_method: Callable[[Any], Any]):
        @wraps(controller_method)
        def http_request_wrapper(self, *args, **kwargs):
            inst, query_params, url_args = generate_controller_model(
                self,
                controller_method,
                args,
                kwargs,
                webid_path,
                action,
                add_path,
                cast,
                map_to_url,
                map_param_names
            )
            return inst.http_url(
                http_method,
                query_params=query_params,
                **url_args
            )
        return http_request_wrapper
    return http_request_decorator


def websocket_request(
    webid_path: str = None,
    action: str = None,
    add_path: Sequence[str] = None,
    cast: Dict[str, AbstractQueryParam] = {},
    map_to_url: Dict[str, str] = {},
    map_param_names: Dict[str, str] = {},
    response_model: BaseContent = PiWebContent
):
    def weboscket_request_decorator(controller_method: Callable[[Any], Any]):
        @wraps(controller_method)
        def websocket_request_wrapper(self, *args, **kwargs):
            inst, query_params, url_args = generate_controller_model(
                self,
                controller_method,
                args,
                kwargs,
                webid_path,
                action,
                add_path,
                cast,
                map_to_url,
                map_param_names
            )
            return inst.websocket_url(
                query_params=query_params,
                **url_args
            )
        return websocket_request_wrapper
    return weboscket_request_decorator