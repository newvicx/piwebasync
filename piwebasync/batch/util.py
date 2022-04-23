import math
from datetime import datetime, timedelta
from typing import Dict, List, Sequence, Tuple

import polars as pl
from piwebasync import APIResponse
from piwebasync.types import JSONPrimitive



def convert_to_frame(
    raw: Dict[str, Dict[str, List[JSONPrimitive]]],
    timezone: str = 'US/Eastern'
) -> pl.DataFrame:
    """
    Convert batch response to dataframe

    The frame is iteratively constructed through a series of
    join operations. The output frame has a single Timestamp
    column and n webid columns for each non empty webid in the
    response
    """
    frames = []
    for webid, data in raw.items():
        # convert data item values to DataFrame
        frame = pl.DataFrame(
            data=data,
            columns=['Timestamp', webid]
        )
        if not frame.is_empty():
            lazy_frame = frame.lazy()
            frames.append(lazy_frame)
    # frame to join on
    seed_frame = pl.DataFrame(columns=['Timestamp'])
    seed_frame = seed_frame.select(pl.col('Timestamp').cast(str))
    seed_frame = seed_frame.lazy()
    for frame in frames:
        seed_frame = seed_frame.join(frame, on='Timestamp', how='outer')
    frame = seed_frame.sort(
        by='Timestamp'
    ).with_column(
        pl.col(
            'Timestamp'
        ).str.strptime(
            pl.Datetime,
            '%Y-%m-%dT%H:%M:%S%.fZ'
        ).dt.with_time_zone(
            timezone
        )
    )
    return frame.collect()

def parse_stream_responses(
    responses: List[APIResponse],
    webids: Sequence[str],
    keep_bad_values: bool = False
) -> Dict[str, Dict[str, List[JSONPrimitive]]]:
    """
    Extract timestamp and value fields from stream responses

    This is a faster (but much less general) method for data
    extraction than `APIResponse.select().`
    """
    unique_webids = set(webids)
    raw = {
        webid: {'Timestamp': [], 'Value': []} for webid in unique_webids
    }
    for webid, response in zip(webids, responses):
        try:
            items = response.items
        except AttributeError:
            # errors returned in response
            continue
        for item in items:
            value = item['Value']
            if isinstance(value, dict):
                value = value['Name']
            timestamp = item['Timestamp']
            good = item['Good']
            # sub items can have errors associated with them
            # this is isolated to a single timestamp
            errors = item.get('Errors')
            if errors is not None or not good:
                if keep_bad_values:
                    raw[webid]['Timestamp'].append(timestamp)
                    raw[webid]['Value'].append(None)
                continue
            raw[webid]['Timestamp'].append(timestamp)
            raw[webid]['Value'].append(value)
    return raw

def split_compressed_range(
    start_time: datetime,
    end_time: datetime,
    ave_frequency: int,
    num_streams: int,
    max_items_per_request: int
) -> Tuple[List[datetime], List[datetime]]:
    """
    Break a single recorded data request into a series of requests over
    a split time range. 
    
    This is required if the totality of the data requested will return
    a total number of items greater than what the PI Web API can support
    over a single request. Without it, data would be missing
    """
    request_time_range = (end_time - start_time).total_seconds()
    items_requested = math.ceil(
        request_time_range / ave_frequency * num_streams
    )
    # 5% buffer as guard
    if .95 * items_requested < max_items_per_request:
        return [start_time], [end_time]
    start_times = []
    end_times = []
    while start_time < end_time:
        start_times.append(start_time)
        # generates next end time at whatever time produces max_rows
        dt = math.floor(
            ave_frequency * max_items_per_request / num_streams * .95
        )
        next_timestamp = start_time + timedelta(seconds=dt)
        if next_timestamp >= end_time:
            start_time = end_time
        else:
            start_time = next_timestamp
        end_times.append(start_time)
    return start_times, end_times

def split_interpolated_range(
    start_time: datetime,
    end_time: datetime,
    interval: timedelta,
    num_streams: int,
    max_items_per_request: int
) -> Tuple[List[datetime], List[datetime]]:
    """
    Break a single interpolated data request into a series of requests over
    a split time range.
    
    This is required if the totality of the data requested will return a
    total number of items greater than what the PI Web API can support
    over a single request. Without it, data would be missing
    """
    request_time_range = (end_time - start_time).total_seconds()
    items_requested = math.ceil(request_time_range / interval.total_seconds() * num_streams)
    # 5% buffer for un-accounted items
    if .95 * items_requested < max_items_per_request:
        return [start_time], [end_time]
    start_times = []
    end_times = []
    while start_time < end_time:
        start_times.append(start_time)
        # generates next end time at whatever time produces max_rows
        dt = math.floor(interval.total_seconds() * max_items_per_request / num_streams * .95)
        next_timestamp = start_time + timedelta(seconds=dt)
        if next_timestamp >= end_time:
            start_time = end_time
        else:
            start_time = next_timestamp
        end_times.append(start_time)
    return start_times, end_times