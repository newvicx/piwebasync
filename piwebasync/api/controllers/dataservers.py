from typing import List, Tuple, Union

from ...types import APIRequestType, ControllerType, QueryStrType

class DataServers:

    """
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/dataserver.html
    """

    CONTROLLER = "dataservers"

    def __init__(self, constructor: ControllerType) -> None:
        self._constructor = constructor

    def list(
        self,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/dataserver/actions/list.html
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
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/dataserver/actions/get.html
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
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/dataserver/actions/getbypath.html
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
    
    def get_by_name(
        self,
        name: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/dataserver/actions/getbyname.html
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

    def get_enumeration_sets(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/dataserver/actions/getenumerationsets.html
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

    def get_license(
        self,
        webid: str,
        module: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/dataserver/actions/getlicense.html
        """

        action = "license"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            module=module,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )
    
    def get_points(
        self,
        webid: str,
        name_filter: QueryStrType = None,
        source_filter: QueryStrType = None,
        start_index: int = None,
        max_count: int = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None,
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/dataserver/actions/getpoints.html
        """

        action = "points"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            name_filter=name_filter,
            source_filter=source_filter,
            start_index=start_index,
            max_count=max_count,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )
