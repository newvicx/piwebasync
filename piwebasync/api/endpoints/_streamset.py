from datetime import datetime, timedelta
from typing import Sequence

from ...core.models._controller import http_request, websocket_request
from ...core.models._params import MultiInstQueryParam, SemiColQueryParam
from ...core.models._url import PiWebHttpUrl, PiWebWebsocketUrl



class StreamSets:

    """
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset.html
    """

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url
        self._controller = 'streamsets'

    @websocket_request(
        action='channel',
        map_to_url={
            'webid': 'webid_path'
        }
    )
    def get_channel(
        self,
        webid: str,
        name_filter: str = None,
        category_name: str = None,
        template_name: str = None,
        search_full_hierarchy: bool = None,
        show_excluded: bool = None,
        show_hidden: bool = None,
        include_initial_values: bool = None,
        heartbeat_rate: int = None,
        web_id_type: str = None
    ) -> PiWebWebsocketUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getchannel.html
        """
    
    @websocket_request(
        action='channel',
        cast={
            'webid': MultiInstQueryParam
        },
        map_param_names={
            'webid': 'web_id'
        }
    )
    def get_channel_adhoc(
        self,
        webid: Sequence[str],
        include_initial_values: bool = None,
        heartbeat_rate: int = None,
        web_id_type: str = None
    ) -> PiWebWebsocketUrl:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getchanneladhoc.html
        """
    
    @http_request(
        "GET",
        action='end',
        cast={
            'selected_fields': SemiColQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )
    def get_end(
        self,
        webid: str,
        name_filter: str = None,
        category_name: str = None,
        template_name: str = None,
        search_full_hierarchy: bool = None,
        show_excluded: bool = None,
        show_hidden: bool = None,
        sort_field: str = None,
        sort_order: str = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getend.html
        """
    
    @http_request(
        "GET",
        action='end',
        cast={
            'webid': MultiInstQueryParam,
            'selected_fields': SemiColQueryParam
        },
        map_param_names={
            'webid': 'web_id'
        }
    )
    def get_end_adhoc(
        self,
        webid: Sequence[str],
        sort_field: str = None,
        sort_order: str = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getendadhoc.html
        """

        action = "end"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            web_id=webid,
            sort_field=sort_field,
            sort_order=sort_order,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )
    
    @http_request(
        "GET",
        action='interpolated',
        cast={
            'selected_fields': SemiColQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )
    def get_interpolated(
        self,
        webid: str,
        start_time: datetime = None,
        end_time: datetime = None,
        time_zone: str = None,
        interval: timedelta = None,
        sync_time: datetime = None,
        sync_time_boundary_type: str = None,
        filter_expression: str = None,
        include_filtered_values: bool = None,
        name_filter: str = None,
        category_name: str = None,
        template_name: str = None,
        search_full_hierarchy: bool = None,
        show_excluded: bool = None,
        show_hidden: bool = None,
        sort_field: str = None,
        sort_order: str = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getinterpolated.html
        """
    
    @http_request(
        "GET",
        action='interpolated',
        cast={
            'webid': MultiInstQueryParam,
            'selected_fields': SemiColQueryParam
        },
        map_param_names={
            'webid': 'web_id'
        }
    )
    def get_interpolated_adhoc(
        self,
        webid: Sequence[str],
        start_time: datetime = None,
        end_time: datetime = None,
        time_zone: str = None,
        interval: str = None,
        sync_time: datetime = None,
        sync_time_boundary_type: str = None,
        filter_expression: str = None,
        include_filtered_values: bool = None,
        sort_field: str = None,
        sort_order: str = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getinterpolatedadhoc.html
        """
    
    @http_request(
        "GET",
        action='interpolatedattimes',
        cast={
            'time': MultiInstQueryParam,
            'selected_fields': SemiColQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )
    def get_interpolated_at_times(
        self,
        webid: str,
        time: Sequence[datetime],
        time_zone: str = None,
        filter_expression: str = None,
        include_filtered_values: bool = None,
        name_filter: str = None,
        category_name: str = None,
        template_name: str = None,
        search_full_hierarchy: bool = None,
        show_excluded: bool = None,
        show_hidden: bool = None,
        sort_order: str = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getinterpolatedattimes.html
        """
    
    @http_request(
        "GET",
        action='interpolatedattimes',
        cast={
            'webid': MultiInstQueryParam,
            'time': MultiInstQueryParam,
            'selected_fields': SemiColQueryParam
        },
        map_param_names={
            'webid': 'web_id'
        }
    )
    def get_interpolated_at_times_adhoc(
        self,
        webid: Sequence[str],
        time: Sequence[datetime],
        time_zone: str = None,
        filter_expression: str = None,
        include_filtered_values: bool = None,
        sort_order: str = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getinterpolatedattimesadhoc.html
        """
    
    @http_request(
        "GET",
        action='joined',
        cast={
            'subordinate_web_id': MultiInstQueryParam,
            'selected_fields': SemiColQueryParam
        }
    )
    def get_joined(
        self,
        base_web_id: str,
        subordinate_web_id: Sequence[str],
        start_time: datetime = None,
        end_time: datetime = None,
        time_zone: str = None,
        boundary_type: str = None,
        filter_expression: str = None,
        include_filtered_values: bool = None,
        max_count: int = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getjoined.html
        """
    
    @http_request(
        "GET",
        action='recorded',
        cast={
            'selected_fields': SemiColQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )
    def get_recorded(
        self,
        webid: str,
        start_time: datetime = None,
        end_time: datetime = None,
        time_zone: str = None,
        boundary_type: str = None,
        filter_expression: str = None,
        include_filtered_values: bool = None,
        name_filter: str = None,
        category_name: str = None,
        template_name: str = None,
        search_full_hierarchy: bool = None,
        show_excluded: bool = None,
        show_hidden: bool = None,
        max_count: int = None,
        sort_field: str = None,
        sort_order: str = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getrecorded.html
        """
    
    @http_request(
        "GET",
        action='recorded',
        cast={
            'webid': MultiInstQueryParam,
            'selected_fields': SemiColQueryParam
        },
        map_param_names={
            'webid': 'web_id'
        }
    )
    def get_recorded_adhoc(
        self,
        webid: Sequence[str],
        start_time: datetime = None,
        end_time: datetime = None,
        time_zone: str = None,
        boundary_type: str = None,
        filter_expression: str = None,
        include_filtered_values: bool = None,
        max_count: int = None,
        sort_field: str = None,
        sort_order: str = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getrecordedadhoc.html
        """

    @http_request(
        "GET",
        action='recordedattime',
        cast={
            'selected_fields': SemiColQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )
    def get_recorded_at_time(
        self,
        webid: str,
        time: datetime,
        time_zone: str = None,
        retrieval_mode: str = None,
        name_filter: str = None,
        category_name: str = None,
        template_name: str = None,
        search_full_hierarchy: bool = None,
        show_excluded: bool = None,
        show_hidden: bool = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getrecordedattime.html
        """
    
    @http_request(
        "GET",
        action='recordedattime',
        cast={
            'webid': MultiInstQueryParam,
            'selected_fields': SemiColQueryParam
        },
        map_param_names={
            'webid': 'web_id'
        }
    )
    def get_recorded_at_time_adhoc(
        self,
        webid: Sequence[str],
        time: datetime,
        time_zone: str = None,
        retrieval_mode: str = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getrecordedattimeadhoc.html
        """
    
    @http_request(
        "GET",
        action='recordedattimes',
        cast={
            'time': MultiInstQueryParam,
            'selected_fields': SemiColQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )
    def get_recorded_at_times(
        self,
        webid: str,
        time: Sequence[datetime],
        time_zone: str = None,
        retrieval_mode: str = None,
        name_filter: str = None,
        category_name: str = None,
        template_name: str = None,
        search_full_hierarchy: bool = None,
        show_excluded: bool = None,
        show_hidden: bool = None,
        sort_order: str = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getrecordedattimes.html
        """

    @http_request(
        "GET",
        action='recordedattimes',
        cast={
            'time': MultiInstQueryParam,
            'webid': MultiInstQueryParam,
            'selected_fields': SemiColQueryParam
        },
        map_param_names={
            'webid': 'web_id'
        }
    )
    def get_recorded_at_times_adhoc(
        self,
        webid: Sequence[str],
        time: Sequence[datetime],
        time_zone: str = None,
        retrieval_mode: str = None,
        sort_order: str = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getrecordedattimesadhoc.html
        """

    @http_request(
        "GET",
        action='summary',
        cast={
            'selected_fields': SemiColQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )
    def get_summary(
        self,
        webid: str,
        start_time: datetime = None,
        end_time: datetime = None,
        time_zone: str = None,
        summary_type: str = None,
        calculation_basis: str = None,
        time_type: str = None,
        summary_duration: str = None,
        sample_type: str = None,
        sample_interval: str = None,
        filter_expression: str = None,
        name_filter: str = None,
        category_name: str = None,
        template_name: str = None,
        search_full_hierarchy: bool = None,
        show_excluded: bool = None,
        show_hidden: bool = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getsummary.html
        """
    
    @http_request(
        "GET",
        action='summary',
        cast={
            'webid': MultiInstQueryParam,
            'selected_fields': SemiColQueryParam
        },
        map_param_names={
            'webid': 'web_id'
        }
    )
    def get_summary_adhoc(
        self,
        webid: Sequence[str],
        start_time: datetime = None,
        end_time: datetime = None,
        time_zone: str = None,
        summary_type: str = None,
        calculation_basis: str = None,
        time_type: str = None,
        summary_duration: str = None,
        sample_type: str = None,
        sample_interval: str = None,
        filter_expression: str = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getsummaryadhoc.html
        """

    @http_request(
        "GET",
        action='value',
        cast={
            'selected_fields': SemiColQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )
    def get_value(
        self,
        webid: str,
        time: datetime,
        time_zone: str = None,
        name_filter: str = None,
        category_name: str = None,
        template_name: str = None,
        search_full_hierarchy: bool = None,
        show_excluded: bool = None,
        show_hidden: bool = None,
        sort_field: str = None,
        sort_order: str = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getvalueadhoc.html
        """

    @http_request(
        "GET",
        action='value',
        cast={
            'webid': MultiInstQueryParam,
            'selected_fields': SemiColQueryParam
        },
        map_param_names={
            'webid': 'web_id'
        }
    )
    def get_value_adhoc(
        self,
        webid: Sequence[str],
        time: datetime,
        time_zone: str = None,
        sort_field: str = None,
        sort_order: str = None,
        selected_fields: Sequence[str] = None,
        web_id_type: str = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getvalueadhoc.html
        """