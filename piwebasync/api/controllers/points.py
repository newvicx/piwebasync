from typing import List, Tuple, Union

from ...types import APIRequestType, ControllerType


class Points:

    """
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/point.html
    """

    CONTROLLER = "points"

    def __init__(self, constructor: ControllerType) -> None:
        self._constructor = constructor

    def get(
        self,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/point/actions/get.html
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
        web_id_type: str = None
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/point/actions/getbypath.html
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

    def get_multiple(
        self,
        webid: Union[List[str], Tuple[str]] = None,
        path: Union[List[str], Tuple[str]] = None,
        include_mode: str = None,
        as_parallel: bool = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> APIRequestType:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/point/actions/getmultiple.html
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
            web_id_type=web_id_type
        )