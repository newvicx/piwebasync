from typing import List, Tuple, Union

from ...types import APIRequestType, ControllerType, QueryStrType

class Attributes:

    """
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/attribute.html
    """

    CONTROLLER = "attributes"

    def __init__(self, constructor: ControllerType) -> None:
        self._constructor = constructor

    def get(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
        associations: Union[List[str], Tuple[str]] = None
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/attribute/actions/get.html
        """

        action = None
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
            associations=associations
        )

    def get_by_path(
        self,
        path: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
        associations: Union[List[str], Tuple[str]] = None
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/attribute/actions/getbypath.html
        """

        action = None
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            path=path,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
            associations=associations
        )

    def get_multiple(
        self,
        webid: Union[List[str], Tuple[str]] = None,
        path: Union[List[str], Tuple[str]] = None,
        include_mode: str = None,
        as_parallel: bool = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
        associations: Union[List[str], Tuple[str]] = None
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/attribute/actions/getmultiple.html
        """

        assert webid is not None or path is not None
        action = "multiple"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            web_id=webid,
            paths=path,
            include_mode=include_mode,
            as_parallel=as_parallel,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
            associations=associations
        )

    def get_value(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/attribute/actions/getvalue.html
        """

        action = "value"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            selected_fields=selected_fields
        )

    def get_attributes(
        self,
        webid: str,
        name_filter: QueryStrType = None,
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
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/element/actions/getattributes.html
        """

        action = "attributes"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
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