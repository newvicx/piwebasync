from typing import List

from ...core.models._content import Empty, PiWebContent



class GetMultiple(PiWebContent):
    """
    Base response class for .get_multiple() on Point,
    Attribute, and Element controllers
    """
    @property
    def webids(self) -> List[str]:
        return [
            item.object.web_id if item.object.web_id is not Empty else None
            for item in self.items
        ]

    @property
    def names(self) -> List[str]:
        return [
            item.object.name if item.object.name is not Empty else None
            for item in self.items
        ]
    
    @property
    def paths(self) -> List[str]:
        return [
            item.object.path if item.object.path is not Empty else None
            for item in self.items
        ]
    
    @property
    def id(self) -> List[str]:
        return [
            item.object.id if item.object.id is not Empty else None
            for item in self.items
        ]

    def raise_for_errors(self):
        errors = {}
        for item in self.items:
            if item.exception.errors:
                identifier = item.identifier or "No Identifier"
                errors[identifier] = item.exception.errors
        if errors:
            raise ContentError(errors)
        

    def get_by_name(self, name: str) -> PiWebContent:
        for item in self.items:
            if item.object.name == name:
                return item
    
    def get_by_path(self, path: str) -> PiWebContent:
        for item in self.items:
            if item.object.path == path:
                return item


class GetMultiplePoints(GetMultiple):
    """
    Response class for Point.get_multiple()
    """
    @property
    def point_types(self) -> List[str]:
        return [
            item.object.point_types
            if item.object.point_types is not Empty else None
            for item in self.items
        ]


class GetMultipleAttributes(GetMultiple):
    """
    Response class for Attribute.get_multiple()
    """
    @property
    def attribute_types(self) -> List[str]:
        return [
            item.object.type if item.object.type is not Empty else None
            for item in self.items
        ]


class GetMultipleElements(GetMultiple):
    """
    Response class for Element.get_multiple()
    """
    @property
    def has_children(self) -> List[bool]:
        return [
            item.object.has_children
            if item.object.has_children is not Empty else None
            for item in self.items
        ]