from typing import Dict, List, Union

import orjson

from ...core.models._content import BaseContent, Empty



class GetStream(BaseContent):
    """
    Base response class for get_interpolated() and get_recorded()
    methods on the Stream controller

    These methods have the potential to return thousands of rows
    which can be slow to process with PiWebContent due the
    recursive interpolation PiWebContent does on the whole response
    content
    """
    class Config:
        extra = "allow"
        json_loads = orjson.loads

    def timestamps(self) -> List[str]:
        return [
            item.get('Timestamp') for item in self.items
            if item.get("Timestamp", Empty) is not Empty
        ]
    
    def values(
        self,
        digital_state_get: str = 'Name'
    ) -> List[Union[str, int, float, bool]]:
        values = []
        for item in self.items:
            value = item.get('Value', Empty)
            if value is not Empty:
                if isinstance(value, dict):
                    values.append(value.get(digital_state_get))
                else:
                    values.append(value)
        return values
    
    def good(self) -> List[bool]:
        return [
            item.get('Good') for item in self.items
            if item.get("Good", Empty) is not Empty
        ]

    def questionable(self) -> List[bool]:
        return [
            item.get('Questionable') for item in self.items
            if item.get("Questionable", Empty) is not Empty
        ]

    def substituted(self) -> List[bool]:
        return [
            item.get('Substituted') for item in self.items
            if item.get("Substituded", Empty) is not Empty
        ]

    def annotated(self) -> List[bool]:
        return [
            item.get('Annotated') for item in self.items
            if item.get("Annotated", Empty) is not Empty
        ]

    def units_abbreviation(self) -> List[str]:
        return [
            item.get('UnitsAbbreviation') for item in self.items
            if item.get("UnitsAbbreviation", Empty) is not Empty
        ]

    def errors(self) -> Dict[str, List[str]]:
        errors = {}
        for item in self.items:
            error = item.get('Errors', Empty)
            if error is not Empty:
                identifier = item.get("Timestamp", "No Timestamp")
                stream_errors = [
                    f"{err_item.get('FieldName')}: " +
                    f"{err_item.get('FieldName')}: ".join(err_item.get('Message'))
                    for err_item in error
                ]
                errors[identifier] = stream_errors
        return errors

    def raise_stream_errors(self):
        errors = self.errors
        if errors:
            raise ContentError(errors)

    def select(
        self,
        *fields: str,
        digital_state_get: str = 'Name'
    ) -> Dict[str, List[Union[str, int, float, bool]]]:
        """
        Select a subset of fields from the response content and convert
        to dataframe compatable dict
        """
        selection = {
            field: [] for field in fields
        }
        for item in self.items:
            for field in fields:
                field_item = item.get(field, Empty)
                if field_item is not Empty:
                    if field == "Value":
                        if isinstance(field_item, dict):
                            selection[field].append(field_item.get(digital_state_get))
                    selection[field].append(field_item)
        return selection
