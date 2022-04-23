from typing import Sequence

from ..models._controller import http_request
from ..models._query import SemiColQueryParam
from ..models._url import PiWebHttpUrl



class AssetServer:

    """
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver.html
    """

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url
        self._controller = 'assetdatabases'

    @http_request(
        "GET",
        cast={
            'selected_fields': SemiColQueryParam
        }
    )
    def list(
        self,
        *,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None,
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/list.html
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
        *,
        webid: str,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None,
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/get.html
        """
    
    @http_request(
        "GET",
        cast={
            'selected_fields': SemiColQueryParam
        }
    )
    def get_by_path(
        self,
        *,
        path: str,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None,
    ) -> PiWebHttpUrl:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/getbypath.html
        """

    @http_request(
        "GET",
        action='assetdatabases',
        cast={
            'selected_fields': SemiColQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )
    def get_databases(
        self,
        *,
        webid: str,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None,
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetserver/actions/getdatabases.html
        """