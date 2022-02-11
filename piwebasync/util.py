import json
import re
import urllib.parse
from datetime import datetime
from functools import partial
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union
)

import orjson
from pydantic import validator

from .exceptions import SerializationError
from .types import (
    ConvertsToStr,
    JSONType,
    StrType
)


def json_dump_content(
    content: JSONType,
    *,
    default: Optional[Callable[[Any], Any]]
) -> str:
    """Helper to decode orjson.dumps which produces bytes"""
    return orjson.dumps(content, default=default).decode()

def json_load_content(content: bytes) -> JSONType:
    """Escapes paths returned by Pi Web API so they can loaded as JSON"""
    content.replace('\\', '\\\\')
    try:
        return orjson.loads(bytes(content, 'utf-8'))
    except json.JSONDecodeError:
        return {}

def normalize_camel_case(key: str) -> None:
    """Convert snake case ``param_a`` to camel case ``ParamA``""" 
    split = key.split('_')
    if len(split) > 1:
        key = ''.join(
            [val.title() for val in split]
        )
        return key
    else:
        return key.title()

def normalize_request_key(key: str) -> str:
    """Convert snake case ``param_a to lower camel case ``paramA``"""
    split = key.split('_')
    if len(split) > 1:
        key = split[0] + ''.join(
            [val.title() for val in split[1:]]
        )
    return key

def normalize_response_key(key: str) -> str:
    """Convert camel case ``ParamA to snake case ``param_a``"""
    split = re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', key)
    if split:
        return '_'.join([val.lower() for val in split])
    return key.lower()

def normalize_request_params(raw_params: Dict[str, StrType]) -> Dict[str, str]:
    """Convert snake case keys to lower camel case and serialize params"""
    return {
        normalize_request_key(key): serialize_to_str(param) for key, param in raw_params.items()
    }

def reuse_validator(key: str, validate_func: Callable[[Any], Any]) -> Any:
    """Helper function for pydantic reuse validator"""
    if isinstance(validate_func, partial):
        validate_func.__name__ = validate_func.func.__name__
    return validator(key, allow_reuse=True, check_fields=False)(validate_func)

def search_response_content(field: str, response: JSONType) -> List[JSONType]:
    """
    Extract field values from nested JSON response. Fields should be
    specified according to hierarchy of the data using dot notation,
    ``Top.Nested.NestedNested``.
    This function groups fields in nested lists by the index in the list
    and returns a list of lists. For example consider the json response below...
    Items: [
        {
            Obj: 1,
            Items: [
                {Value: 1},
                {Value: 2},
            ]
        },
        {
           Obj: 2,
            Items: [
                {Value: 3},
                {Value: 4},
            ]
        }
    ]
    A field value of "Items.Items.Value" will produce the following output...
    [[1, 2], [3, 4]]
    """

    def extract_nested_fields_from_list(
        nested_fields: List[str],
        subset: List[JSONType],
        level: int = 0
    ) -> List[JSONType]:
        items = []
        for item in subset:
            if isinstance(item, dict):
                items.append(extract_nested_fields_from_dict(nested_fields, item, level))
            elif isinstance(item, list):
                items.append(extract_nested_fields_from_list(nested_fields, item, level))
            else:
                items.append(item)
        return items

    def extract_nested_fields_from_dict(
        nested_fields: List[str],
        subset: dict,
        level: int = 0
    ) -> Union[JSONType, List[JSONType]]:
        nested_field = nested_fields[level]
        try:
            item = subset[nested_field]
        except KeyError:
            level -= 1
            return
        if isinstance(item, list):
            level += 1
            return extract_nested_fields_from_list(nested_fields, item, level)
        elif isinstance(item, dict):
            level += 1
            return extract_nested_fields_from_dict(nested_fields, item, level)
        else:
            level -= 1
            return item
            
    nested_fields = field.split(".")
    nested_field = nested_fields.pop(0)
    try:
        subset = response[nested_field]
        if isinstance(subset, dict) and nested_fields:
            return extract_nested_fields_from_dict(nested_fields, subset)
        elif isinstance(subset, list) and nested_fields:
            return extract_nested_fields_from_list(nested_fields, subset)
        else:
            return subset
    except KeyError:
        return

def serialize_arbitrary_to_str(obj: ConvertsToStr) -> str:
    """Serialize arbitrary objects with a __str__ method. datetime converts to isoformat"""
    if isinstance(obj, datetime):
        return obj.isoformat("T")
    elif hasattr(obj, "__str__"):
        return str(obj)
    else:
        raise SerializationError(
            f"Cannot serialize object of type {type(obj)} to str"
        )

def serialize_to_str(obj: StrType) -> str:
    """Serialize objects to be used as query params to str"""
    if not obj:
        return
    elif isinstance(obj, str):
        return obj
    elif isinstance(obj, bytes):
        return obj.decode()
    # tuples are converted to list
    elif isinstance(obj, (list, tuple)):
        return [serialize_arbitrary_to_str(item) for item in obj]
    elif isinstance(obj, (datetime, float, int)):
        return serialize_arbitrary_to_str(obj)
    else:
        raise TypeError(
            f"Invalid type to serialize '{type(obj)}'"
        )

def serialize_multi_instance(
    key: str,
    params: Union[
        List[ConvertsToStr],
        Tuple[ConvertsToStr]
    ]
) -> str:
    """
    Serializes Pi Web API parameters that can be specified multiple times
    such as 'webId' for StreamSetAdHoc controller
    """
    assert isinstance(params, (list, tuple))
    serialized: Union[List[str], Tuple[str]] = serialize_to_str(params)
    if len(serialized) > 1:
        return f"{serialized.pop(0)}&{key}=" + f"&{key}=".join(serialized)
    else:
        return f"{serialized.pop(0)}"

def serialize_semi_colon_separated(
    params: Union[
        List[ConvertsToStr],
        Tuple[ConvertsToStr]
    ]
) -> str:
    """
    Serializes Pi Web API parameters that can have multiple values
    separated by semi colons such as 'selectedFields' for most controllers
    """
    assert isinstance(params, (list, tuple))
    return ";".join(serialize_to_str(params))
