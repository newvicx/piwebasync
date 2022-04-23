from datetime import datetime
from typing import Sequence

from ..models._controller import http_request
from ..models._query import MultiInstQueryParam ,SemiColQueryParam
from ..models._url import PiWebHttpUrl



class AssetDatabase:

    """
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase.html
    """

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url
        self._controller = 'assetdatabases'

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
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/get.html
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
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/getbypath.html
        """
    
    @http_request(
        "GET",
        action='elements',
        cast={
            'selected_fields': SemiColQueryParam,
            'associations': SemiColQueryParam
        },
        map_to_url={'webid': 'webid_path'}
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
        selected_fields: Sequence[str] = None,
        web_id_type: str = None,
        associations: Sequence[str] = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/getelements.html
        """
    
    @http_request(
        "GET",
        action='eventframes',
        cast={
            'selected_fields': SemiColQueryParam,
            'severity': MultiInstQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )
    def get_event_frames(
        self,
        webid: str,
        search_mode: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        name_filter: str = None,
        referenced_element_name_filter: str = None,
        category_name: str = None,
        template_name: str = None,
        referenced_element_template_name: str = None,
        severity: Sequence[str] = None,
        can_be_acknowledged: bool = None,
        is_acknowleged: bool = None,
        search_full_hierarchy: bool = None,
        sort_field: str = None,
        sort_order: str = None,
        start_index: int = None,
        max_count: int = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/assetdatabase/actions/geteventframes.html
        """