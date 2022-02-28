from datetime import datetime
from typing import List, Tuple, Union

from ...types import APIRequestType, ControllerType, QueryStrType

class EventFrames:

    """
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe.html
    """

    CONTROLLER = "eventframes"

    def __init__(self, constructor: ControllerType) -> None:
        self._constructor = constructor

    def get(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe/actions/get.html
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
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe/actions/getbypath.html
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
    
    def acknowledge(
        self,
        webid: str
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe/actions/acknowledge.html
        """

        action = "acknowledge"
        return self._constructor._build_request(
            method="PATCH",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid
        )

    def execute_search_by_attribute(
        self,
        search_id: str,
        search_mode: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        name_filter: QueryStrType = None,
        referenced_element_name_filter: QueryStrType = None,
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
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe/actions/executesearchbyattribute.html
        """

        action = "searchbyattribute"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            add_path=[search_id],
            search_mode=search_mode,
            start_time=start_time,
            end_time=end_time,
            name_filter=name_filter,
            referenced_element_name_filter=referenced_element_name_filter,
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
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe/actions/findeventframeattributes.html
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

    def get_annotation_attachment_media_by_id(
        self,
        webid: str,
        id: str,
        disposition: str = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe/actions/get.html
        """

        action = "annotations"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            add_path=[id, "attachment", "media"],
            disposition=disposition,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    def get_annotation_attachment_media_data_by_id(
        self,
        webid: str,
        id: str,
        disposition: str = None
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe/actions/getannotationattachmentmediadatabyid.html
        """

        action = "annotations"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            add_path=[id, "attachment", "media", "mediadata"],
            disposition=disposition
        )

    def get_annotation_attachment_media_metadata_by_id(
        self,
        webid: str,
        id: str,
        disposition: str = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe/actions/getannotationattachmentmediametadatabyid.html
        """

        action = "annotations"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            add_path=[id, "attachment", "media", "metadata"],
            disposition=disposition,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    def get_annotation_by_id(
        self,
        webid: str,
        id: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe/actions/getannotationbyid.html
        """

        action = "annotations"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            add_path=[id],
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )
    
    def get_annotations(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe/actions/getannotations.html
        """

        action = "annotations"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            selected_fields=selected_fields,
            web_id_type=web_id_type
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
        trait_category: Union[List[str], Tuple[str]] = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe/actions/getattributes.html
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
            trait_many=trait,
            trait_category_many=trait_category
        )
    
    def get_categories(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe/actions/getcategories.html
        """

        action = "categories"
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
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe/actions/geteventframes.html
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
    
    def get_event_frames_query(
        self,
        database_web_id: str = None,
        query: QueryStrType = None,
        start_index: int = None,
        max_count: int = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe/actions/geteventframesquery.html
        """

        action = "search"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            database_web_id=database_web_id,
            query=query,
            start_index=start_index,
            max_count=max_count,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
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
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe/actions/getmultiple.html
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
    
    def get_referenced_elements(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
        associations: Union[List[str], Tuple[str]] = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe/actions/getreferencedelements.html
        """

        action = "referencedelements"
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

    def get_security(
        self,
        webid: str,
        user_identity: Union[List[str], Tuple[str]] = None,
        force_refresh: bool = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe/actions/getsecurity.html
        """

        action = "security"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            user_identity_many=user_identity,
            force_refresh=force_refresh,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )
    
    def get_security_entries(
        self,
        webid: str,
        name_filter: QueryStrType = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe/actions/getsecurityentries.html
        """

        action = "securityentries"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            name_filter=name_filter,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
        )

    def get_security_entry_by_name(
        self,
        webid: str,
        name: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/eventframe/actions/getsecurityentrybyname.html
        """

        action = "securityentries"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
            add_path = [name]
        )