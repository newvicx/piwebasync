import asyncio
import math
from datetime import datetime, timedelta
from typing import List, Sequence

import polars as pl

from piwebasync import APIRequest, Controller, HTTPClient
from piwebasync.exceptions import IntervalError
from .util import (
    convert_to_frame,
    parse_stream_responses,
    split_compressed_range,
    split_interpolated_range,
)



class Batch:

    def __init__(
        self,
        controller: Controller,
        client: HTTPClient,
        max_items_per_request: int = 150000
    ) -> None:
        
        self._controller = controller
        self._client = client
        self._max_items_per_request = max_items_per_request
    
    async def interpolated(
        self,
        webids: Sequence[str],
        start_time: datetime,
        end_time: datetime = None,
        interval: timedelta = None,
        keep_bad_values: bool = False
    ) -> pl.DataFrame:

        selected_fields = [
            'Items.Timestamp',
            'Items.Good',
            'Items.Value'
        ]
        end_time = end_time or datetime.now()
        interval = interval or timedelta(seconds=3600)
        if interval.total_seconds() < 1:
            raise IntervalError("PI Web API does not support sub second intervals")
        str_interval = f"{interval.total_seconds()} seconds"
        start_times, end_times = split_interpolated_range(
            start_time,
            end_time,
            interval,
            1,
            self._max_items_per_request
        )
        requests = []
        for webid in webids:
            for start_time, end_time in zip(start_times, end_times):
                request = self._controller.streams.get_interpolated(
                    webid,
                    start_time=start_time,
                    end_time=end_time,
                    interval=str_interval,
                    selected_fields=selected_fields
                )
                requests.append(request)
        return await self._get_frame_from_streams(
            requests,
            keep_bad_values
        )
    
    async def compressed(
        self,
        webids: Sequence[str],
        start_time: datetime,
        end_time: datetime = None,
        ave_frequency: int = 10,
        keep_bad_values: bool = False
    ) -> pl.DataFrame:

        selected_fields = [
            'Items.Timestamp',
            'Items.Good',
            'Items.Value'
        ]
        end_time = end_time or datetime.now()
        
        start_times, end_times = split_compressed_range(
            start_time,
            end_time,
            ave_frequency,
            1,
            self._max_items_per_request
        )
        requests = []
        for webid in webids:
            for start_time, end_time in zip(start_times, end_times):
                request = self._controller.streams.get_recorded(
                    webid,
                    start_time=start_time,
                    end_time=end_time,
                    boundary_type='outside',
                    max_count=math.floor(self._max_items_per_request / 1),
                    selected_fields=selected_fields
                )
                requests.append(request)
        return await self._get_frame_from_streams(
            requests,
            keep_bad_values
        )

    async def _get_frame(
        self,
        requests: List[APIRequest],
        keep_bad_values: bool
    ) -> pl.DataFrame:
        """
        Make requests and build batch frame
        """
        webids = [request.webid for request in requests]
        dispatch = [self._client.request(request) for request in requests]
        responses = await asyncio.gather(*dispatch)
        raw = parse_stream_responses(responses, webids, keep_bad_values=keep_bad_values)
        frame = convert_to_frame(raw)
        return frame