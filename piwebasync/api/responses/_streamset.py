from typing import Dict, List

import orjson

from ...core.models._content import BaseContent, Empty



class GetStreamSet(BaseContent):
    """
    Base response class for get_interpolated() and get_recorded()
    methods on the StreamSet controller

    These methods have the potential to return thousands of rows
    which can be slow to process with PiWebContent due the
    recursive interpolation PiWebContent does on the whole response
    content
    """
    class Config:
        extra = "allow"
        json_load = orjson.loads

    def webids(self):
        return [
            item.get('WebId') for item in self.items
            if item.get('WebId', Empty) is not Empty
        ]

    def names(self):
        return [
            item.get('Name') for item in self.items
            if item.get('Name', Empty) is not Empty
        ]

    def paths(self):
        return [
            item.get('Path') for item in self.items
            if item.get('Path', Empty) is not Empty
        ]

    def timestamps(self):
        items = self.items.get('Items', Empty())
        return [
            item.get('Timestamp') for item in items
            if item.get("Timestamp", Empty) is not Empty
        ]
    
    def values(self, digital_state_get: str = 'Name'):
        values = []
        items = self.items.get('Items', Empty())
        for item in items:
            value = item.get('Value', Empty)
            if value is not Empty:
                if isinstance(value, dict):
                    values.append(value.get(digital_state_get))
                else:
                    values.append(value)
        return values
    
    def good(self):
        items = self.items.get('Items', Empty())
        return [
            item.get('Good') for item in items
            if item.get("Good", Empty) is not Empty
        ]

    def questionable(self):
        items = self.items.get('Items', Empty())
        return [
            item.get('Questionable') for item in items
            if item.get("Questionable", Empty) is not Empty
        ]

    def substituted(self):
        items = self.items.get('Items', Empty())
        return [
            item.get('Substituted') for item in items
            if item.get("Substituded", Empty) is not Empty
        ]

    def annotated(self):
        items = self.items.get('Items', Empty())
        return [
            item.get('Annotated') for item in items
            if item.get("Annotated", Empty) is not Empty
        ]

    def units_abbreviation(self):
        items = self.items.get('Items', Empty())
        return [
            item.get('UnitsAbbreviation') for item in items
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

    def select(
        self,
        *fields: str,
        streamset_delimeter: str = 'WebId',
        digital_state_get: str = 'Name'
    ):
        """
        Select a subset of fields from the response content and convert
        to dataframe compatable dict
        """
        if streamset_delimeter.lower() not in ['webid', 'name', 'path']:
            raise ValueError(f"Invalid streamset delimeter '{streamset_delimeter}'")
        dispatch = {
            'webid': self.webids,
            'name': self.names,
            'path': self.paths
        }
        delimeter = dispatch[streamset_delimeter.lower()]
        selection = {
            delim: {field: [] for field in fields} for delim in delimeter()
        }
        for item in self.items:
            delim = item.get(streamset_delimeter, Empty)
            if delim is not Empty:
                sub_select = selection[delim]
                sub_items = item.get('Items', [])
                for sub_item in sub_items:
                    for field in fields:
                        field_item = sub_item.get(field, Empty)
                        if field_item is not Empty:
                            if field == "Value":
                                if isinstance(field_item, dict):
                                    sub_select[field].append(field_item.get(digital_state_get))
                            sub_select[field].append(field_item)
        return selection