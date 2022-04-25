from typing import Sequence

from ...core.models._controller import http_request
from ...core.models._params import SemiColQueryParam
from ...core.models._url import PiWebHttpUrl



class DataServers:

    """
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/dataserver.html
    """

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url
        self._controller = 'dataservers'

    @http_request(
        "GET",
        cast={
            'selected_fields': SemiColQueryParam
        }
    )
    def list(
        self,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None,
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/dataserver/actions/list.html
        """

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
        web_id_type: str = None,
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/dataserver/actions/get.html
        """

    @http_request(
        "GET",
        cast={
            'selected_fields': SemiColQueryParam
        }
    )
    def get_by_path(
        self,
        path: str,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None,
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/dataserver/actions/getbypath.html
        """
    
    @http_request(
        "GET",
        cast={
            'selected_fields': SemiColQueryParam
        }
    )
    def get_by_name(
        self,
        name: str,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None,
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/dataserver/actions/getbyname.html
        """

    @http_request(
        "GET",
        action='points',
        cast={
            'selected_fields': SemiColQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )   
    def get_points(
        self,
        webid: str,
        name_filter: str = None,
        source_filter: str = None,
        start_index: int = None,
        max_count: int = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None,
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/dataserver/actions/getpoints.html
        """