from datetime import datetime
from typing import List, Tuple, Union

from .base import BaseController


class Streams(BaseController):

    """
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream.html
    """

    CONTROLLER = "streams"

    @classmethod
    def get_channel(
        cls,
        webid: str,
        include_initial_values: bool = None,
        heartbeat_rate: int = None,
        web_id_type: str = None
    ) -> "Streams":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getchannel.html
        """

        action = "channel"
        return cls(
            method="GET",
            protocol="Websocket",
            action=action,
            webid=webid,
            include_initial_values=include_initial_values,
            heartbeat_rate=heartbeat_rate,
            web_id_type=web_id_type
        )
    
    @classmethod
    def get_end(
        cls,
        webid: str,
        desired_units: str = None,
        selected_fields: Union[List[str], Tuple[str]] = None
    ) -> "Streams":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getend.html
        """

        action = "end"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            webid=webid,
            desired_units=desired_units,
            selected_fields=selected_fields
        )
    
    @classmethod
    def get_interpolated(
        cls,
        webid: str,
        start_time: datetime = None,
        end_time: datetime = None,
        time_zone: str = None,
        interval: str = None,
        sync_time: datetime = None,
        sync_time_boundary_type: str = None,
        desired_units: str = None,
        filter_expression: str = None,
        include_filtered_values: bool = None,
        selected_fields: Union[List[str], Tuple[str]] = None
    ) -> "Streams":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getinterpolated.html
        """

        action = "interpolated"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            webid=webid,
            start_time=start_time,
            end_time=end_time,
            time_zone=time_zone,
            interval=interval,
            sync_time=sync_time,
            sync_time_boundary_type=sync_time_boundary_type,
            desired_units=desired_units,
            filter_expression=filter_expression,
            include_filtered_values=include_filtered_values,
            selected_fields=selected_fields
        )
    
    @classmethod
    def get_interpolated_at_times(
        cls,
        webid: str,
        time: Union[List[datetime], Tuple[datetime]],
        time_zone: str = None,
        desired_units: str = None,
        filter_expression: str = None,
        include_filtered_values: bool = None,
        sort_order: str = None,
        selected_fields: Union[List[str], Tuple[str]] = None
    ) -> "Streams":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getinterpolatedattimes.html
        """

        action="interpolatedattimes"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            webid=webid,
            times=time,
            time_zone=time_zone,
            desired_units=desired_units,
            filter_expression=filter_expression,
            include_filtered_values=include_filtered_values,
            sort_order=sort_order,
            selected_fields=selected_fields
        )
    
    @classmethod
    def get_recorded(
        cls,
        webid: str,
        start_time: datetime = None,
        end_time: datetime = None,
        time_zone: str = None,
        boundary_type: str = None,
        desired_units: str = None,
        filter_expression: str = None,
        include_filtered_values: bool = None,
        max_count: int = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        associations: Union[List[str], Tuple[str]] = None
    ) -> "Streams":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getrecorded.html
        """

        action="recorded"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            webid=webid,
            start_time=start_time,
            end_time=end_time,
            time_zone=time_zone,
            boundary_type=boundary_type,
            desired_units=desired_units,
            filter_expression=filter_expression,
            include_filtered_values=include_filtered_values,
            max_count=max_count,
            selected_fields=selected_fields,
            associations=associations
        )

    @classmethod
    def get_recorded_at_time(
        cls,
        webid: str,
        time: datetime,
        time_zone: str = None,
        retrieval_mode: str = None,
        desired_units: str = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        associations: Union[List[str], Tuple[str]] = None
    ) -> "Streams":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getrecordedattime.html
        """

        action = "recordedattime"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            webid=webid,
            time=time,
            time_zone=time_zone,
            retrieval_mode=retrieval_mode,
            desired_units=desired_units,
            selected_fields=selected_fields,
            associations=associations
        )
    
    @classmethod
    def get_recorded_at_times(
        cls,
        webid: str,
        time: Union[List[datetime], Tuple[datetime]],
        time_zone: str = None,
        retrieval_mode: str = None,
        desired_units: str = None,
        sort_order: str = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        associations: Union[List[str], Tuple[str]] = None
    ) -> "Streams":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getrecordedattimes.html
        """

        action="recordedattimes"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            webid=webid,
            times=time,
            time_zone=time_zone,
            retrieval_mode=retrieval_mode,
            desired_units=desired_units,
            sort_order=sort_order,
            selected_fields=selected_fields,
            associations=associations
        )

    @classmethod
    def get_summary(
        cls,
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
        selected_fields: Union[List[str], Tuple[str]] = None,
    ) -> "Streams":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getsummary.html
        """

        action="summary"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            webid=webid,
            start_time=start_time,
            end_time=end_time,
            time_zone=time_zone,
            summary_type=summary_type,
            calculation_basis=calculation_basis,
            time_type=time_type,
            summary_duration=summary_duration,
            sample_type=sample_type,
            sample_interval=sample_interval,
            filter_expression=filter_expression,
            selected_fields=selected_fields
        )

    @classmethod
    def get_value(
        cls,
        webid: str,
        time: datetime,
        time_zone: str = None,
        desired_units: str = None,
        selected_fields: Union[List[str], Tuple[str]] = None
    ) -> "Streams":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/stream/actions/getvalueadhoc.html
        """

        action="value"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            webid=webid,
            time=time,
            time_zone=time_zone,
            desired_units=desired_units,
            selected_fields=selected_fields
        )