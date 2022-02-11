from typing import List, Tuple, Union

from .base import BaseController


class Points(BaseController):

    """
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/point.html
    """

    CONTROLLER = "points"

    @classmethod
    def get(
        cls,
        webid: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> "Points":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/point/actions/get.html
        """

        action = None
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            webid=webid,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    @classmethod
    def get_by_path(
        cls,
        path: str,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> "Points":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/point/actions/getbypath.html
        """

        action = None
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            path=path,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    @classmethod
    def get_multiple(
        cls,
        webid: Union[List[str], Tuple[str]] = None,
        path: Union[List[str], Tuple[str]] = None,
        include_mode: str = None,
        as_parallel: bool = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> "Points":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/point/actions/getmultiple.html
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
            web_id_type=web_id_type
        )