from typing import Sequence

from ..models._controller import http_request
from ..models._query import MultiInstQueryParam ,SemiColQueryParam
from ..models._url import PiWebHttpUrl



class Element:

    """
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/element.html
    """

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url
        self._controller = 'elements'

    @http_request(
        "GET",
        cast={
            'selected_fields': SemiColQueryParam,
            'associations': SemiColQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )
    def get(
        self,
        webid: str,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None,
        associations: Sequence[str] = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/element/actions/get.html
        """

    @http_request(
        "GET",
        cast={
            'selected_fields': SemiColQueryParam,
            'associations': SemiColQueryParam
        }
    )
    def get_by_path(
        self,
        path: str,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None,
        associations: Sequence[str] = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/element/actions/getbypath.html
        """

    @http_request(
        "GET",
        action='multiple',
        cast={
            'web_id': MultiInstQueryParam,
            'path': MultiInstQueryParam,
            'selected_fields': SemiColQueryParam,
            'associations': SemiColQueryParam
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
        web_id_type: str = None,
        associations: Sequence[str] = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/element/actions/getmultiple.html
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
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/element/actions/getelements.html
        """

    @http_request(
        "GET",
        action='attributes',
        cast={
            'selected_fields': SemiColQueryParam,
            'associations': SemiColQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )
    def get_attributes(
        self,
        webid: str,
        name_filter: str = None,
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
        selected_fields: Sequence[str] = None,
        web_id_type: str = None,
        associations: Sequence[str] = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/element/actions/getattributes.html
        """