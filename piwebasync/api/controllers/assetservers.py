from typing import List, Tuple, Union

from ...types import APIRequestType, ControllerType, QueryStrType

class AssetServers:

    """
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver.html
    """

    CONTROLLER = "assetservers"

    def __init__(self, constructor: ControllerType) -> None:
        self._constructor = constructor

    def list(
        self,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/list.html
        """

        action = None
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    def get(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/get.html
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
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/getbypath.html
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

    def get_analysis_rule_plugins(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/getanalysisruleplugins.html
        """

        action = "analysisruleplugins"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    def get_by_name(
        self,
        name: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/getbyname.html
        """

        action = None
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            name=name,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )
    
    def get_databases(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/getdatabases.html
        """

        action = "assetdatabases"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    def get_notification_contact_templates(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/getnotificationcontacttemplates.html
        """

        action = "notificationcontacttemplates"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    def get_notification_plugins(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/getnotificationplugins.html
        """

        action = "notificationplugins"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            selected_fields=selected_fields,
            web_id_type=web_id_type
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
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/getsecurity.html
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
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/getsecurityentries.html
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
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/getsecurityentrybyname.html
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

    def get_security_identities(
        self,
        webid: str,
        query: QueryStrType = None,
        field: str = None,
        sort_field: str = None,
        sort_order: str = None,
        max_count: int = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/getsecurityidentities.html
        """

        action = "securityidentities"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            query=query,
            field=field,
            sort_field=sort_field,
            sort_order=sort_order,
            max_count=max_count,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
        )

    def get_security_identities_for_user(
        self,
        webid: str,
        user_identity: str = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/getsecurityidentitiesforuser.html
        """

        action = "securityidentities"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            user_identity=user_identity,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
        )

    def get_security_mappings(
        self,
        webid: str,
        query: QueryStrType = None,
        field: str = None,
        sort_field: str = None,
        sort_order: str = None,
        max_count: int = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/getsecuritymappings.html
        """

        action = "securitymappings"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            query=query,
            field=field,
            sort_field=sort_field,
            sort_order=sort_order,
            max_count=max_count,
            selected_fields=selected_fields,
            web_id_type=web_id_type,
        )

    def get_time_rule_plugins(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/gettimeruleplugins.html
        """

        action = "timeruleplugins"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    def get_unit_classes(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/getunitclasses.html
        """

        action = "unitclasses"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    

    
