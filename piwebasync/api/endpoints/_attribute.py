from typing import Sequence

from ...core.models._controller import http_request
from ...core.models._params import MultiInstQueryParam, SemiColQueryParam
from ...core.models._url import PiWebHttpUrl



class Attribute:

    """
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/attribute.html
    """

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url
        self._controller = 'attributes'

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
        *,
        webid: str,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None,
        associations: Sequence[str] = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/attribute/actions/get.html
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
        *,
        path: str,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None,
        associations: Sequence[str] = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/attribute/actions/getbypath.html
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
        map_param_names={'webid': 'web_id'}
    )
    def get_multiple(
        self,
        *,
        webid: Sequence[str] = None,
        path: Sequence[str] = None,
        include_mode: str = None,
        as_parallel: bool = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None,
        associations: Sequence[str] = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/attribute/actions/getmultiple.html
        """
    
    @http_request(
        "GET",
        action='attributes',
        cast={
            'selected_fields': SemiColQueryParam,
            'associations': SemiColQueryParam,
            'trait': MultiInstQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )
    def get_attributes(
        self,
        *,
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
        associations: Sequence[str] = None,
        trait: Sequence[str] = None,
        trait_category: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/element/actions/getattributes.html
        """