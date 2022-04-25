import copy
from abc import ABC, abstractproperty
from datetime import datetime, timedelta
from inspect import isclass
from typing import Any, Dict, Sequence, Union

from pydantic import BaseModel, validator

from .._serialization import serialize_lower_camel_case


class StrImplemented:
    """
    Type validator for a user defined type that implements
    the __str__ method
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> Union[
        str,
        int,
        float,
        datetime,
        timedelta
    ]:
        if isinstance(
            value,
            (
                str,
                int,
                float,
                datetime,
                timedelta
            )
        ):
            return value
        if isclass(value):
            raise ValueError(f"Uninstantiated type {value.__name__}")
        try:
            if type(value).__str__ is not object.__str__:
                return value.__str__()
        except AttributeError:
            pass
        raise ValueError("Value must have user implemented '__str__' method")


class QueryValue(BaseModel):
    """
    A single query parameter value

    Validates that any value is...
    - A string
    - An integer
    - A float
    - A datetime.datetime
    - A datetime.timedelta
    - A StrImplemented
    * StrImplemented is an arbitrary type, user defined type
    that implements the __str__ method
    """
    value: Union[
        str,
        int,
        float,
        datetime,
        timedelta,
        StrImplemented,
    ]

    @validator('value')
    def _serialize_value(cls, value: Union[
        str,
        int,
        float,
        datetime,
        timedelta,
        StrImplemented,
    ]) -> Union[str, int, float]:
        """
        Serialize value to one of str, int, or float
        """
        if isinstance(value, datetime):
            return value.isoformat(sep='T')
        if isinstance(value, timedelta):
            return f"{value.total_seconds()} seconds"
        return value


class AbstractQueryParam(ABC, BaseModel):
    """
    Abstract class for a query parameter

    All query parameters must implement the `serialized`
    property
    """
    @validator('value', pre=True, each_item=True, check_fields=False)
    def _prep_value(cls, value: Any) -> Dict[str, Any]:
        # allows for passing value=Any into subclass rather than
        # value = {'value': Any}
        return {'value': value}

    @abstractproperty
    def serialized(self):
        pass


class QueryParam(AbstractQueryParam):
    """
    Single value query paramater

    Accepts any valid type which can be converted to a QueryValue
    """
    field_name: str
    value: QueryValue

    @property
    def serialized(self):
        serialize_lower_camel_case(self.field_name), self.value.value


class SemiColQueryParam(AbstractQueryParam):
    """
    Query parameter which can have multiple instances separated
    by a semi-colon

    Accepts a sequence of valid types which can be converted
    to a QueryValue. On serialization, query values are joined
    with ';'
    """
    field_name: str
    value: Sequence[QueryValue]

    @property
    def serialized(self):
        serialized_values = ';'.join([val.value for val in self.value])
        return serialize_lower_camel_case(self.field_name), serialized_values


class MultiInstQueryParam(AbstractQueryParam):
    """
    Query parameter which can be specified multiple times
    in the same request

    Accepts a sequence of valid types which can be converted
    to a QueryValue. On serialization, query values are joined
    with '&{field_name}={QueryValue}'
    """
    field_name: str
    value: Sequence[QueryValue]

    @property
    def serialized(self):
        value_copy = copy.copy(self.value)
        if len(value_copy) > 1:
            serialized_values = (
                f"{value_copy.pop(0).value}&{serialize_lower_camel_case(self.field_name)}=" +
                f"&{serialize_lower_camel_case(self.field_name)}=".join(
                    [val.value for val in value_copy]
                )
            )
        else:
            serialized_values = value_copy.pop(0)
        return serialize_lower_camel_case(self.field_name), serialized_values