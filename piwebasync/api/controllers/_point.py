from typing import Sequence

from ..models._controller import http_request
from ..models._query import MultiInstQueryParam, SemiColQueryParam
from ..models._url import PiWebHttpUrl



class Points:

    """
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/point.html
    """

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url
        self._controller = 'points'

    @http_request(
        "GET",
        cast={
            'selected_fields': SemiColQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )
    def get(
        self,
        webid: str,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/point/actions/get.html
        """

    @http_request(
        "GET",
        cast={
            'selected_fields': SemiColQueryParam,
        }
    )
    def get_by_path(
        self,
        path: str,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/point/actions/getbypath.html
        """

    @http_request(
        "GET",
        action='multiple',
        cast={
            'web_id': MultiInstQueryParam,
            'path': MultiInstQueryParam,
            'selected_fields': SemiColQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )
    def get_multiple(
        self,
        webid: Sequence[str] = None,
        path: Sequence[str] = None,
        include_mode: str = None,
        as_parallel: bool = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/point/actions/getmultiple.html
        """

    @http_request(
        "GET",
        cast={
            'name': MultiInstQueryParam,
            'selected_fields': SemiColQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )
    def get_attributes(
        self,
        webid: str,
        name: Sequence[str] = None,
        name_filter: str = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/point/actions/getattributes.html
        """