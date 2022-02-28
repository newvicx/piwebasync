from datetime import datetime
from typing import List, Tuple, Union

from ...types import APIRequestType, ControllerType, QueryStrType

class AssetDatabases:

    """
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase.html
    """

    CONTROLLER = "assetdatabases"

    def __init__(self, constructor: ControllerType) -> None:
        self._constructor = constructor

    def get(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/get.html
        """

        action = None
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    def get_by_path(
        self,
        path: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/getbypath.html
        """

        action = None
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            path=path,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    def find_analyses(
        self,
        webid: str,
        field: str = None,
        query: QueryStrType = None,
        sort_field: str = None,
        start_index: int = None,
        sort_order: str = None,
        max_count: int = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/findanalyses.html
        """

        action = "analyses"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            field=field,
            query=query,
            sort_field=sort_field,
            sort_order=sort_order,
            start_index=start_index,
            max_count=max_count,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
        )

    def find_element_attributes(
        self,
        webid: str,
        element_name_filter: QueryStrType = None,
        element_description_filter: QueryStrType = None,
        element_category: str = None,
        element_template: str = None,
        element_type: str = None,
        attribute_name_filter: QueryStrType = None,
        attribute_description_filter: QueryStrType = None,
        attribute_category: str = None,
        attribute_type: str = None,
        search_full_hierarchy: bool = None,
        sort_field: str = None,
        sort_order: str = None,
        start_index: int = None,
        max_count: int = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
        associations: Union[List[str], Tuple[str]] = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/findelementattributes.html
        """

        action = "elementattributes"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            element_name_filter=element_name_filter,
            element_description_filter=element_description_filter,
            element_category=element_category,
            element_template=element_template,
            element_type=element_type,
            attribute_name_filter=attribute_name_filter,
            attribute_description_filter=attribute_description_filter,
            attribute_category=attribute_category,
            attribute_type=attribute_type,
            search_full_hierarchy=search_full_hierarchy,
            sort_field=sort_field,
            sort_order=sort_order,
            start_index=start_index,
            max_count=max_count,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
            associations=associations
        )

    def find_event_frame_attributes(
        self,
        webid: str,
        search_mode: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        event_frame_name_filter: QueryStrType = None,
        event_frame_description_filter: QueryStrType = None,
        referenced_element_name_filter: QueryStrType = None,
        event_frame_category: str = None,
        event_frame_template: str = None,
        attribute_name_filter: QueryStrType = None,
        attribute_description_filter: QueryStrType = None,
        attribute_category: str = None,
        attribute_type: str = None,
        search_full_hierarchy: bool = None,
        sort_field: str = None,
        sort_order: str = None,
        start_index: int = None,
        max_count: int = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
        associations: Union[List[str], Tuple[str]] = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/findeventframeattributes.html
        """

        action = "eventframeattributes"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            search_mode=search_mode,
            start_time=start_time,
            end_time=end_time,
            event_frame_name_filter=event_frame_name_filter,
            event_frame_description_filter=event_frame_description_filter,
            referenced_element_name_filter=referenced_element_name_filter,
            event_frame_category=event_frame_category,
            event_frame_template=event_frame_template,
            attribute_name_filter=attribute_name_filter,
            attribute_description_filter=attribute_description_filter,
            attribute_category=attribute_category,
            attribute_type=attribute_type,
            search_full_hierarchy=search_full_hierarchy,
            sort_field=sort_field,
            sort_order=sort_order,
            start_index=start_index,
            max_count=max_count,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
            associations=associations
        )

    def get_analysis_categories(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/getanalysiscategories.html
        """

        action = "analysiscategories"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    def get_analysis_templates(
        self,
        webid: str,
        field: str = None,
        query: QueryStrType = None,
        sort_field: str = None,
        sort_order: str = None,
        max_count: int = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/getanalysistemplates.html
        """

        action = "analysistemplates"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            field=field,
            query=query,
            sort_field=sort_field,
            sort_order=sort_order,
            max_count=max_count,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
        )

    def get_attribute_categories(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/getattributecategories.html
        """

        action = "attributecategories"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    def get_element_categories(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/getelementcategories.html
        """

        action = "elementcategories"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    def get_elements(
        self,
        webid: str,
        name_filter: str = None,
        description_filter: str = None,
        category_name: str = None,
        template_name: str = None,
        element_type: str = None,
        search_full_hierarchy: bool = None,
        sort_field: str = None,
        sort_order: str = None,
        start_index: int = None,
        max_count: int = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
        associations: Union[List[str], Tuple[str]] = None
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/getelements.html
        """

        action ="elements"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            name_filter=name_filter,
            description_filter=description_filter,
            category_name=category_name,
            template_name=template_name,
            element_type=element_type,
            search_full_hierarchy=search_full_hierarchy,
            sort_field=sort_field,
            sort_order=sort_order,
            start_index=start_index,
            max_count=max_count,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
            associations=associations
        )

    def get_element_templates(
        self,
        webid: str,
        field: str = None,
        query: QueryStrType = None,
        sort_field: str = None,
        sort_order: str = None,
        max_count: int = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/getelementtemplates.html
        """

        action = "elementtemplates"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            field=field,
            query=query,
            sort_field=sort_field,
            sort_order=sort_order,
            max_count=max_count,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
        )

    def get_enumeration_sets(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/getenumerationsets.html
        """

        action = "enumerationsets"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    def get_event_frames(
        self,
        webid: str,
        search_mode: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        name_filter: QueryStrType = None,
        referenced_element_name_filter: QueryStrType = None,
        category_name: str = None,
        template_name: str = None,
        referenced_element_template_name: str = None,
        severity: Union[List[str], Tuple[str]] = None,
        can_be_acknowledged: str = None,
        is_acknowleged: str = None,
        search_full_hierarchy: bool = None,
        sort_field: str = None,
        sort_order: str = None,
        start_index: int = None,
        max_count: int = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/geteventframes.html
        """

        action = "eventframes"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            search_mode=search_mode,
            start_time=start_time,
            end_time=end_time,
            name_filter=name_filter,
            referenced_element_name_filter=referenced_element_name_filter,
            category_name=category_name,
            template_name=template_name,
            referenced_element_template_name=referenced_element_template_name,
            severity_many=severity,
            can_be_acknowledged=can_be_acknowledged,
            is_acknowleged=is_acknowleged,
            search_full_hierarchy=search_full_hierarchy,
            sort_field=sort_field,
            sort_order=sort_order,
            start_index=start_index,
            max_count=max_count,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
        )

    def get_referenced_elements(
        self,
        webid: str,
        name_filter: QueryStrType = None,
        description_filter: QueryStrType = None,
        category_name: str = None,
        template_name: str = None,
        element_type: str = None,
        sort_field: str = None,
        sort_order: str = None,
        start_index: int = None,
        max_count: int = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
        associations: Union[List[str], Tuple[str]] = None
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/getreferencedelements.html
        """

        action = "referencedelements"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            name_filter=name_filter,
            description_filter=description_filter,
            category_name=category_name,
            template_name=template_name,
            element_type=element_type,
            sort_field=sort_field,
            sort_order=sort_order,
            start_index=start_index,
            max_count=max_count,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
            associations=associations
        )

    def get_security(
        self,
        webid: str,
        security_item: Union[List[str], Tuple[str]] = None,
        user_identity: Union[List[str], Tuple[str]] = None,
        force_refresh: bool = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/getsecurity.html
        """

        action = "security"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            security_item_many=security_item,
            user_identity_many=user_identity,
            force_refresh=force_refresh,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )
    
    def get_security_entries(
        self,
        webid: str,
        security_item: str = None,
        name_filter: QueryStrType = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/getsecurityentries.html
        """

        action = "securityentries"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            security_item=security_item,
            name_filter=name_filter,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
        )

    def get_security_entry_by_name(
        self,
        webid: str,
        name: str,
        security_item: str = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/getsecurityentrybyname.html
        """

        action = "securityentries"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            security_item=security_item,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
            add_path = [name]
        )

    def get_table_categories(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/gettablecategories.html
        """

        action = "tablecategories"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )