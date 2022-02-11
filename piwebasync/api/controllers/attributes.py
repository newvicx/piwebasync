from typing import List, Tuple, Union

from .base import BaseController


class Attributes(BaseController):

    """
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/attribute.html
    """

    CONTROLLER = "Attributes"

    @classmethod
    def get(
        cls,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
        associations: Union[List[str], Tuple[str]] = None
    ) -> "Attributes":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/attribute/actions/get.html
        """

        action = None
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            webid=webid,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
            associations=associations
        )

    @classmethod
    def get_by_path(
        cls,
        path: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
        associations: Union[List[str], Tuple[str]] = None
    ) -> "Attributes":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/attribute/actions/getbypath.html
        """

        action = None
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            path=path,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
            associations=associations
        )

    @classmethod
    def get_multiple(
        cls,
        webid: Union[List[str], Tuple[str]] = None,
        path: Union[List[str], Tuple[str]] = None,
        include_mode: str = None,
        as_parallel: bool = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
        associations: Union[List[str], Tuple[str]] = None
    ) -> "Attributes":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/attribute/actions/getmultiple.html
        """

        assert webid is not None or path is not None
        action = "multiple"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            web_id=webid,
            paths=path,
            include_mode=include_mode,
            as_parallel=as_parallel,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
            associations=associations
        )

    @classmethod
    def get_value(
        cls,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None
    ) -> "Attributes":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/attribute/actions/getvalue.html
        """

        action = "value"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            webid=webid,
            selected_fields=selected_fields
        )

    @classmethod
    def get_attributes(
        cls,
        webid: str,
        name_filter: str = None,
        category_name: str = None,
        template_name: str = None,
        value_type: str = None,
        search_full_hierarchy: bool = None,
        sort_field: str = None,
        sort_order: str = None,
        start_index: int = None,
        show_excluded: bool = None,
        show_hidden: bool = None,
        max_count: int = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
        associations: Union[List[str], Tuple[str]] = None,
        trait: Union[List[str], Tuple[str]] = None,
        trait_category: str = None
    ) -> "Attributes":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/element/actions/getattributes.html
        """

        action = "attributes"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            webid=webid,
            name_filter=name_filter,
            category_name=category_name,
            template_name=template_name,
            value_type=value_type,
            search_full_hierarchy=search_full_hierarchy,
            sort_field=sort_field,
            sort_order=sort_order,
            start_index=start_index,
            show_excluded=show_excluded,
            show_hidden=show_hidden,
            max_count=max_count,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
            associations=associations,
            trait=trait,
            trait_category=trait_category
        )