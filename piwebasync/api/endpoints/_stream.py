from datetime import datetime, timedelta
from typing import Sequence

from ...core.models._controller import http_request, websocket_request
from ...core.models._params import MultiInstQueryParam, SemiColQueryParam
from ...core.models._url import PiWebHttpUrl, PiWebWebsocketUrl



class Stream:

    """
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream.html
    """

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url
        self._controller = 'streams'

    @websocket_request(
        action='channel',
        map_to_url={
            'webid': 'webid_path'
        }
    )
    def get_channel(
        self,
        webid: str,
        include_initial_values: bool = None,
        heartbeat_rate: int = None,
        web_id_type: str = None
    ) -> PiWebWebsocketUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getchannel.html
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
        desired_units: str = None,
        selected_fields: Sequence[str] = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getend.html
        """
    
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
        desired_units: str = None,
        filter_expression: str = None,
        include_filtered_values: bool = None,
        selected_fields: Sequence[str] = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getinterpolated.html
        """
    
    @http_request(
        "GET",
        action='interpolatedattimes',
        cast={
            'selected_fields': SemiColQueryParam,
            'time': MultiInstQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )
    def get_interpolated_at_times(
        self,
        webid: str,
        time: Sequence[datetime],
        time_zone: str = None,
        desired_units: str = None,
        filter_expression: str = None,
        include_filtered_values: bool = None,
        sort_order: str = None,
        selected_fields: Sequence[str] = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getinterpolatedattimes.html
        """
    
    @http_request(
        "GET",
        action='recorded',
        cast={
            'selected_fields': SemiColQueryParam,
            'associations': SemiColQueryParam
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
        desired_units: str = None,
        filter_expression: str = None,
        include_filtered_values: bool = None,
        max_count: int = None,
        selected_fields: Sequence[str] = None,
        associations: Sequence[str] = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getrecorded.html
        """

    @http_request(
        "GET",
        action='recordedattime',
        cast={
            'selected_fields': SemiColQueryParam,
            'associations': SemiColQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )
    def get_recorded_at_time(
        self,
        webid: str,
        time: datetime,
        time_zone: str = None,
        retrieval_mode: str = None,
        desired_units: str = None,
        selected_fields: Sequence[str] = None,
        associations: Sequence[str] = None
    ) -> PiWebHttpUrl:

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getrecordedattime.html
        """

        action = "recordedattime"
        return self._constructor._build_request(
            method="GET",
            protocol="HTTP",
            controller=self.CONTROLLER,
            action=action,
            webid=webid,
            time=time,
            time_zone=time_zone,
            retrieval_mode=retrieval_mode,
            desired_units=desired_units,
            selected_fields=selected_fields,
            associations=associations
        )
    
    @http_request(
        "GET",
        action='recordedattimes',
        cast={
            'time': MultiInstQueryParam,
            'selected_fields': SemiColQueryParam,
            'associations': SemiColQueryParam
        },
        map_to_url={'webid': 'webid_path'}
    )
    def get_recorded_at_times(
        self,
        webid: str,
        time: Sequence[datetime],
        time_zone: str = None,
        retrieval_mode: str = None,
        desired_units: str = None,
        sort_order: str = None,
        selected_fields: Sequence[str] = None,
        associations: Sequence[str] = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getrecordedattimes.html
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
        selected_fields: Sequence[str] = None,
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getsummary.html
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
        desired_units: str = None,
        selected_fields: Sequence[str] = None
    ) -> PiWebHttpUrl:
        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getvalueadhoc.html
        """