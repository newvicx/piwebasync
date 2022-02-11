from datetime import datetime
from typing import List, Tuple, Union

from .base import BaseController


class StreamSets(BaseController):

    """
    https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset.html
    """

    CONTROLLER = "streamsets"

    @classmethod
    def get_channel(
        cls,
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
    ) -> "StreamSets":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getchannel.html
        """

        action = "channel"
        return cls(
            method="GET",
            protocol="Websocket",
            action=action,
            webid=webid,
            name_filter=name_filter,
            category_name=category_name,
            template_name=template_name,
            search_full_hierarchy=search_full_hierarchy,
            show_excluded=show_excluded,
            show_hidden=show_hidden,
            include_initial_values=include_initial_values,
            heartbeat_rate=heartbeat_rate,
            web_id_type=web_id_type
        )
    
    @classmethod
    def get_channel_adhoc(
        cls,
        webid: Union[List[str], Tuple[str]],
        include_initial_values: bool = None,
        heartbeat_rate: int = None,
        web_id_type: str = None
    ) -> "StreamSets":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getchanneladhoc.html
        """

        action = "channel"
        return cls(
            method="GET",
            protocol="Websocket",
            action=action,
            web_id=webid,
            include_initial_values=include_initial_values,
            heartbeat_rate=heartbeat_rate,
            web_id_type=web_id_type
        )
    
    @classmethod
    def get_end(
        cls,
        webid: str,
        name_filter: str = None,
        category_name: str = None,
        template_name: str = None,
        search_full_hierarchy: bool = None,
        show_excluded: bool = None,
        show_hidden: bool = None,
        sort_field: str = None,
        sort_order: str = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> "StreamSets":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getend.html
        """

        action = "end"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            webid=webid,
            name_filter=name_filter,
            category_name=category_name,
            template_name=template_name,
            search_full_hierarchy=search_full_hierarchy,
            show_excluded=show_excluded,
            show_hidden=show_hidden,
            sort_field=sort_field,
            sort_order=sort_order,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )
    
    @classmethod
    def get_end_adhoc(
        cls,
        webid: Union[List[str], Tuple[str]],
        sort_field: str = None,
        sort_order: str = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> "StreamSets":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getendadhoc.html
        """

        action = "end"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            web_id=webid,
            sort_field=sort_field,
            sort_order=sort_order,
            selected_fields=selected_fields,
            web_id_type=web_id_type
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
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> "StreamSets":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getinterpolated.html
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
            filter_expression=filter_expression,
            include_filtered_values=include_filtered_values,
            name_filter=name_filter,
            category_name=category_name,
            template_name=template_name,
            search_full_hierarchy=search_full_hierarchy,
            show_excluded=show_excluded,
            show_hidden=show_hidden,
            sort_field=sort_field,
            sort_order=sort_order,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )
    
    @classmethod
    def get_interpolated_adhoc(
        cls,
        webid: Union[List[str], Tuple[str]],
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
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> "StreamSets":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getinterpolatedadhoc.html
        """

        action = "interpolated"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            web_id=webid,
            start_time=start_time,
            end_time=end_time,
            time_zone=time_zone,
            interval=interval,
            sync_time=sync_time,
            sync_time_boundary_type=sync_time_boundary_type,
            filter_expression=filter_expression,
            include_filtered_values=include_filtered_values,
            sort_field=sort_field,
            sort_order=sort_order,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )
    
    @classmethod
    def get_interpolated_at_times(
        cls,
        webid: str,
        time: Union[List[datetime], Tuple[datetime]],
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
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> "StreamSets":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getinterpolatedattimes.html
        """

        action = "interpolatedattimes"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            webid=webid,
            times=time,
            time_zone=time_zone,
            filter_expression=filter_expression,
            include_filtered_values=include_filtered_values,
            name_filter=name_filter,
            category_name=category_name,
            template_name=template_name,
            search_full_hierarchy=search_full_hierarchy,
            show_excluded=show_excluded,
            show_hidden=show_hidden,
            sort_order=sort_order,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )
    
    @classmethod
    def get_interpolated_at_times_adhoc(
        cls,
        webid: Union[List[str], Tuple[str]],
        time: Union[List[datetime], Tuple[datetime]],
        time_zone: str = None,
        filter_expression: str = None,
        include_filtered_values: bool = None,
        sort_order: str = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> "StreamSets":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getinterpolatedattimesadhoc.html
        """

        action = "interpolatedattimes"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            web_id=webid,
            times=time,
            time_zone=time_zone,
            filter_expression=filter_expression,
            include_filtered_values=include_filtered_values,
            sort_order=sort_order,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )
    
    @classmethod
    def get_joined(
        cls,
        base_web_id: str,
        subordinate_web_id: Union[List[str], Tuple[str]],
        start_time: datetime = None,
        end_time: datetime = None,
        time_zone: str = None,
        boundary_type: str = None,
        filter_expression: str = None,
        include_filtered_values: bool = None,
        max_count: int = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> "StreamSets":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getjoined.html
        """

        action = "joined"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            base_web_id=base_web_id,
            subordinate_web_id=subordinate_web_id,
            start_time=start_time,
            end_time=end_time,
            time_zone=time_zone,
            boundary_type=boundary_type,
            filter_expression=filter_expression,
            include_filtered_values=include_filtered_values,
            max_count=max_count,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )
    
    @classmethod
    def get_recorded(
        cls,
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
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> "StreamSets":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getrecorded.html
        """

        action = "recorded"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            webid=webid,
            start_time=start_time,
            end_time=end_time,
            time_zone=time_zone,
            boundary_type=boundary_type,
            filter_expression=filter_expression,
            include_filtered_values=include_filtered_values,
            name_filter=name_filter,
            category_name=category_name,
            template_name=template_name,
            search_full_hierarchy=search_full_hierarchy,
            show_excluded=show_excluded,
            show_hidden=show_hidden,
            max_count=max_count,
            sort_field=sort_field,
            sort_order=sort_order,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )
    
    @classmethod
    def get_recorded_adhoc(
        cls,
        webid: Union[List[str], Tuple[str]],
        start_time: datetime = None,
        end_time: datetime = None,
        time_zone: str = None,
        boundary_type: str = None,
        filter_expression: str = None,
        include_filtered_values: bool = None,
        max_count: int = None,
        sort_field: str = None,
        sort_order: str = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> "StreamSets":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getrecordedadhoc.html
        """

        action = "recorded"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            web_id=webid,
            start_time=start_time,
            end_time=end_time,
            time_zone=time_zone,
            boundary_type=boundary_type,
            filter_expression=filter_expression,
            include_filtered_values=include_filtered_values,
            max_count=max_count,
            sort_field=sort_field,
            sort_order=sort_order,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    @classmethod
    def get_recorded_at_time(
        cls,
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
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> "StreamSets":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getrecordedattime.html
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
            name_filter=name_filter,
            category_name=category_name,
            template_name=template_name,
            search_full_hierarchy=search_full_hierarchy,
            show_excluded=show_excluded,
            show_hidden=show_hidden,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )
    
    @classmethod
    def get_recorded_at_time_adhoc(
        cls,
        webid: Union[List[str], Tuple[str]],
        time: datetime,
        time_zone: str = None,
        retrieval_mode: str = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> "StreamSets":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getrecordedattimeadhoc.html
        """

        action = "recordedattime"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            web_id=webid,
            time=time,
            time_zone=time_zone,
            retrieval_mode=retrieval_mode,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )
    
    @classmethod
    def get_recorded_at_times(
        cls,
        webid: str,
        time: Union[List[datetime], Tuple[datetime]],
        time_zone: str = None,
        retrieval_mode: str = None,
        name_filter: str = None,
        category_name: str = None,
        template_name: str = None,
        search_full_hierarchy: bool = None,
        show_excluded: bool = None,
        show_hidden: bool = None,
        sort_order: str = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> "StreamSets":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getrecordedattimes.html
        """

        action = "recordedattimes"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            webid=webid,
            times=time,
            time_zone=time_zone,
            retrieval_mode=retrieval_mode,
            name_filter=name_filter,
            category_name=category_name,
            template_name=template_name,
            search_full_hierarchy=search_full_hierarchy,
            show_excluded=show_excluded,
            show_hidden=show_hidden,
            sort_order=sort_order,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    @classmethod
    def get_recorded_at_times_adhoc(
        cls,
        webid: Union[List[str], Tuple[str]],
        time: Union[List[datetime], Tuple[datetime]],
        time_zone: str = None,
        retrieval_mode: str = None,
        sort_order: str = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> "StreamSets":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getrecordedattimesadhoc.html
        """

        action = "recordedattimes"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            web_id=webid,
            times=time,
            time_zone=time_zone,
            retrieval_mode=retrieval_mode,
            sort_order=sort_order,
            selected_fields=selected_fields,
            web_id_type=web_id_type
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
        name_filter: str = None,
        category_name: str = None,
        template_name: str = None,
        search_full_hierarchy: bool = None,
        show_excluded: bool = None,
        show_hidden: bool = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> "StreamSets":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getsummary.html
        """

        action = "summary"
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
            name_filter=name_filter,
            category_name=category_name,
            template_name=template_name,
            search_full_hierarchy=search_full_hierarchy,
            show_excluded=show_excluded,
            show_hidden=show_hidden,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )
    
    @classmethod
    def get_summary_adhoc(
        cls,
        webid: Union[List[str], Tuple[str]],
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
        web_id_type: str = None
    ) -> "StreamSets":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getsummaryadhoc.html
        """

        action = "summary"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            web_id=webid,
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
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    @classmethod
    def get_value(
        cls,
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
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> "StreamSets":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getvalueadhoc.html
        """

        action = "value"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            webid=webid,
            time=time,
            time_zone=time_zone,
            name_filter=name_filter,
            category_name=category_name,
            template_name=template_name,
            search_full_hierarchy=search_full_hierarchy,
            show_excluded=show_excluded,
            show_hidden=show_hidden,
            sort_field=sort_field,
            sort_order=sort_order,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )

    @classmethod
    def get_value_adhoc(
        cls,
        webid: Union[List[str], Tuple[str]],
        time: datetime,
        time_zone: str = None,
        sort_field: str = None,
        sort_order: str = None,
        selected_fields: Union[List[str], Tuple[str]] = None,
        web_id_type: str = None
    ) -> "StreamSets":

        """
        https://docs.osisoft.com/bundle/pi-web-api-reference/page/help/controllers/streamset/actions/getvalueadhoc.html
        """

        action = "value"
        return cls(
            method="GET",
            protocol="HTTP",
            action=action,
            web_id=webid,
            time=time,
            time_zone=time_zone,
            sort_field=sort_field,
            sort_order=sort_order,
            selected_fields=selected_fields,
            web_id_type=web_id_type
        )