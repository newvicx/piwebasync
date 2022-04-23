from typing import List, Union

from ..models._response import Empty, PiWebContent



class GetPointAttributes(PiWebContent):
    """
    Response class for Point.get_attributes()
    """
    @property
    def names(self) -> List[str]:
        return [
            item.name if item.name is not Empty else None
            for item in self.items
        ]
    
    @property
    def values(self) -> List[Union[str, int, float, bool]]:
        return [
            item.value if item.value is not Empty else None
            for item in self.items
        ]
    
    def get_by_name(self, name: str) -> PiWebContent:
        for item in self.items:
            if item.name == name:
                return item


class GetItems(PiWebContent):
    """
    Base class for response models which have the schema
    {
        Items: [
            Attr: Val
        ]
    }
    Not to be used for Stream and Streamset controllers
    """
    @property
    def webids(self) -> List[str]:
        return [
            item.web_id if item.web_id is not Empty else None
            for item in self.items
        ]
    
    @property
    def names(self) -> List[str]:
        return [
            item.name if item.name is not Empty else None
            for item in self.items
        ]
    
    @property
    def paths(self) -> List[str]:
        return [
            item.path if item.path is not Empty else None
            for item in self.items
        ]
    
    @property
    def id(self) -> List[str]:
        return [
            item.id if item.id is not Empty else None
            for item in self.items
        ]

    def get_by_name(self, name: str) -> PiWebContent:
        for item in self.items:
            if item.name == name:
                return item
    
    def get_by_path(self, path: str) -> PiWebContent:
        for item in self.items:
            if item.path == path:
                return item


class GetAssetServerItems(GetItems):
    """
    Response class for AssetServer.list()
    """


class GetDataServerItems(GetItems):
    """
    Response class for DataServer.list()
    """


class GetAssetDatabaseItems(GetItems):
    """
    Response class for AssetServer.get_databases()
    """


class GetElementItems(GetItems):
    """
    Response class for AssetDatabase.get_elements()
    and Element.get_elements()
    """
    @property
    def has_children(self) -> List[bool]:
        return [
            item.has_children if item.has_children is not Empty else None
            for item in self.items
        ]


class GetAttributeItems(GetItems):
    """
    Response class for Element.get_attributes()
    and Attribute.get_attributes()
    """
    @property
    def attribute_types(self) -> List[str]:
        return [
            item.type if item.type is not Empty else None
            for item in self.items
        ]
    
    @property
    def has_children(self) -> List[bool]:
        return [
            item.has_children if item.has_children is not Empty else None
            for item in self.items
        ]


class GetPointItems(GetItems):
    """
    Response class for DataServer.get_points()
    """
    @property
    def point_types(self) -> List[str]:
        return [
            item.point_types if item.point_types is not Empty else None
            for item in self.items
        ]