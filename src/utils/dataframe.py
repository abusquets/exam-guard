import datetime
import logging
import math
import time
from typing import List, Literal, Optional, Tuple, Union

import pandas as pd

from config import settings


logger = logging.getLogger(f'{settings.APP_LOGGER_NAME}.dataframe')


def to_timestamp_seconds(year: int, month: int, day: int, hour: int, minute: int, second: int) -> int:
    return int(time.mktime(time.strptime(f'{year}-{month}-{day} {hour}:{minute}:{second}', '%Y-%m-%d %H:%M:%S')))


def to_datetime_string(timestamp: int) -> str:
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))


def to_datetime(timestamp: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(timestamp)


def expand_to_3_hours(
    example: List[Tuple[int, float]],  # ts, value
    *,
    hours: int = 3,
    unit: Literal[1, 60] = 1,  # seconds
) -> List[Tuple[int, float]]:  # ts, value
    if not example:
        return []

    timestamps = []
    duration_seconds = hours * 60 * 60  # 3 hours in seconds

    i = 0
    ts = example[0][0]
    while ts < example[0][0] + duration_seconds:
        ts = example[0][0] + (i * unit)
        timestamps.append(ts)
        i += 1

    values = [example[i % len(example)][1] for i in range(len(timestamps))]
    return list(zip(timestamps, values))


def expand_to_3_hours_pandas(
    data: List[Tuple[int, float]],
    *,
    hours: int = 3,
    unit: Literal[1, 60] = 1,  # seconds
) -> List[Tuple[int, float]]:
    if not data:
        return []

    df = pd.DataFrame(data, columns=['ts', 'value'])

    # Convert timestamps to datetime if they aren't already
    df['ts'] = pd.to_datetime(df['ts'], unit='s', utc=False)

    # Calculate total duration in desired unit
    total_duration = pd.Timedelta(hours=hours)

    # Create a range of timestamps with the specified unit frequency
    _unit = datetime.timedelta(seconds=unit)
    timestamps = pd.date_range(start=df['ts'].min(), end=df['ts'].min() + total_duration, freq=_unit)
    values = (list(df['value']) * math.ceil(len(timestamps) / len(data)))[: len(timestamps)]

    timestamps = timestamps.astype(int) // 10**9
    return list(zip(list(timestamps), values))


def extract_outliers(
    start_value: Union[int, float],
    data: List[Tuple[int, Union[int, float]]],
    threshold: Union[int, float],
    interval: int,
) -> Optional[List[Tuple[int, float]]]:
    # TODO: Refactor to support more than one outlier
    # See notebook version for more details
    logger.debug('data', extra={'data': data})
    itimes = 0
    value_threshold = start_value + (start_value * threshold / 100)
    threshold_data = []
    for j in range(len(data)):
        value = data[j][1]
        increment = (value / start_value * 100) - 100
        logger.debug(
            f'Comparing value `{value}` againts value_threshold `{value_threshold}`'
            f' increment `{increment}%`'
            f' itimes `{itimes}`'
        )
        if value > value_threshold:
            threshold_data.append(data[j])
            itimes += 1
        else:
            itimes = 0

    if itimes >= interval:
        logger.warning('Suspicious data')
        return threshold_data
    return None
