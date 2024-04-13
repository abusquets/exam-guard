import datetime
import logging
import time
from typing import List, Tuple, Union

from config import settings


logger = logging.getLogger(f'{settings.APP_LOGGER_NAME}.generate_data')


def check_data(
    data: List[Tuple[int, float]], start_value: Union[int, float], threshold: Union[int, float], interval: int
) -> bool:
    i = 0
    threshold = start_value + (start_value * threshold / 100)
    for j in range(len(data)):
        value = data[j][1]
        if value > threshold:
            i += 1
        if i == interval:
            return True
    raise Exception(f'Data is not correct {value} {i}')


def populate_missing_seconds(data: List[Tuple[int, float]]) -> List[Tuple[int, float]]:
    data_x_seconds = []

    n = len(data)
    for i in range(n - 1):  # Iterate up to the second last element
        start_time, start_value = data[i]
        end_time, end_value = data[i + 1]

        elapsed_seconds = end_time - start_time
        if elapsed_seconds <= 0:
            continue  # Skip if start and end times are the same or out of order

        increment_per_second = (end_value - start_value) / elapsed_seconds

        # Add the start point
        data_x_seconds.append((start_time, start_value))

        # Generate data for each second between start and end
        for seconds_passed in range(1, elapsed_seconds):
            new_time = start_time + seconds_passed
            new_value = start_value + (increment_per_second * seconds_passed)
            data_x_seconds.append((new_time, new_value))

    # Add the last point
    if n > 0:
        data_x_seconds.append(data[-1])

    return data_x_seconds


def generate_blood_pressure_data(
    interval_changes: List[float], start: int = 120, interval: int = 30
) -> List[Tuple[int, float]]:
    data = []
    for i in range(len(interval_changes)):
        factor = interval_changes[i] / 100
        value = start + (start * factor)
        data.append((i * interval, value))
    return data


def generate_heart_rate_data(
    interval_changes: List[float], start: int = 60, interval: int = 30
) -> List[Tuple[int, float]]:
    data = []
    for i in range(len(interval_changes)):
        factor = interval_changes[i] / 100
        value = start + (start * factor)
        data.append((i * interval, value))
    return data


def nine_minutes_blood_pressure() -> List[Tuple[int, float]]:
    interval_changes = [
        # 0 minutes
        0,
        # 0 minutes 30 seconds
        0.5,
        # 1 minute 0 seconds
        0.5,
        # 1 minute 30 seconds
        1,
        # 2 minutes 0 seconds
        4,
        # 2 minutes 30 seconds
        20,
        # 3 minutes 0 seconds
        22,
        # 3 minutes 30 seconds
        22,
        # 4 minutes 0 seconds
        20.05,
        # 4 minutes 30 seconds
        21,
        # 5 minutes 0 seconds
        15,
        # 5 minutes 30 seconds
        10,
        # 6 minutes 0 seconds
        8,
        # 6 minutes 30 seconds
        7,
        # 7 minutes 0 seconds
        4,
        # 7 minutes 30 seconds
        2.5,
        # 8 minutes 0 seconds
        1,
        # 8 minutes 30 seconds
        0.5,
        # 9 minutes 0 seconds
        0,
    ]
    data = generate_blood_pressure_data(interval_changes)
    ret = populate_missing_seconds(data)
    check_data(ret, 120, 20, 120)
    return ret


def nine_minutes_heart_rate() -> List[Tuple[int, float]]:
    interval_changes = [
        # 0 minutes
        0,
        # 0 minutes 30 seconds
        0,
        # 1 minute 0 seconds
        0,
        # 1 minute 30 seconds
        0,
        # 2 minutes 0 seconds
        0,
        # 2 minutes 30 seconds
        2,
        # 3 minutes 0 seconds
        4,
        # 3 minutes 30 seconds
        11,
        # 4 minutes 0 seconds
        31,
        # 4 minutes 30 seconds
        32,
        # 5 minutes 0 seconds
        33,
        # 5 minutes 30 seconds
        31.5,
        # 6 minutes 0 seconds
        18,
        # 6 minutes 30 seconds
        10,
        # 7 minutes 0 seconds
        5,
        # 7 minutes 30 seconds
        3,
        # 8 minutes 0 seconds
        0.5,
        # 8 minutes 30 seconds
        0,
        # 9 minutes 0 seconds
        0,
    ]
    data = generate_heart_rate_data(interval_changes)
    ret = populate_missing_seconds(data)
    check_data(ret, 60, 30, 90)
    return ret


def expand_to_3_hours(example: List[Tuple[int, float]], duration: int = 3) -> List[Tuple[int, float]]:
    data = []
    ts_start = int(time.time())
    num_examples = len(example)
    duration_seconds = duration * 60 * 60  # 3 hours in seconds

    for i in range(duration_seconds):
        ts = ts_start + i
        sample_index = i % num_examples
        data.append((ts, example[sample_index][1]))

    logger.info(f'DIFF: {data[-1][0] - ts_start}')
    logger.info(f'FROM: {datetime.datetime.fromtimestamp(data[0][0])}')
    logger.info(f'TO: {datetime.datetime.fromtimestamp(data[-1][0])}')

    return data
