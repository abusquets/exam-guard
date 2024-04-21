import datetime
from typing import Callable, List, Tuple

import pandas as pd
import pytest

from utils.dataframe import expand_to_3_hours, expand_to_3_hours_pandas, to_datetime, to_timestamp_seconds


EXAMPLE_DATA_SECONDS = [
    (to_timestamp_seconds(2021, 1, 1, 0, 0, 1), 10.5),
    (to_timestamp_seconds(2021, 1, 1, 0, 0, 2), 20.5),
    (to_timestamp_seconds(2021, 1, 1, 0, 0, 3), 30.5),
]

EXAMPLE_DATA_MINUTES = [
    (to_timestamp_seconds(2021, 1, 1, 0, 0, 0), 10.5),
    (to_timestamp_seconds(2021, 1, 1, 0, 1, 0), 20.5),
    (to_timestamp_seconds(2021, 1, 1, 0, 2, 0), 30.5),
]


@pytest.mark.parametrize(
    'fnc,in_data',
    [
        (expand_to_3_hours, EXAMPLE_DATA_SECONDS),
        (expand_to_3_hours_pandas, EXAMPLE_DATA_SECONDS),
        (expand_to_3_hours, EXAMPLE_DATA_MINUTES),
        (expand_to_3_hours_pandas, EXAMPLE_DATA_MINUTES),
    ],
)
def test_expand_to_3_hours_basic(fnc: Callable, in_data: List[Tuple[int, float]]) -> None:
    result = fnc(in_data)

    assert isinstance(result, list)
    assert all(isinstance(item, tuple) and len(item) == 2 for item in result)

    timestamps = [item[0] for item in result]
    assert all(timestamps[i] < timestamps[i + 1] for i in range(len(timestamps) - 1))


@pytest.mark.parametrize(
    'fnc,in_data',
    [
        (expand_to_3_hours, EXAMPLE_DATA_SECONDS),
        (expand_to_3_hours_pandas, EXAMPLE_DATA_SECONDS),
        (expand_to_3_hours, EXAMPLE_DATA_MINUTES),
        (expand_to_3_hours_pandas, EXAMPLE_DATA_MINUTES),
    ],
)
def test_expand_end_datetime(fnc: Callable, in_data: List[Tuple[int, float]]) -> None:
    result = fnc(in_data)
    end = to_datetime(result[0][0]) + datetime.timedelta(seconds=60 * 60 * 3)
    assert to_datetime(result[-1][0]).isoformat() == end.isoformat()


@pytest.mark.parametrize('in_data', [EXAMPLE_DATA_SECONDS, EXAMPLE_DATA_MINUTES])
def test_same_data(in_data: List[Tuple[int, float]]) -> None:
    data1 = expand_to_3_hours(in_data)
    data2 = expand_to_3_hours_pandas(in_data)
    assert data1[0][0] == data2[0][0]
    assert data1[-1][0] == data2[-1][0]

    df1 = pd.DataFrame(data1, columns=['ts', 'value'])
    df2 = pd.DataFrame(data1, columns=['ts', 'value'])

    assert df1.equals(df2)
    assert data1 == data2


@pytest.mark.parametrize(
    'fnc,in_data',
    [
        (expand_to_3_hours, EXAMPLE_DATA_SECONDS),
        (expand_to_3_hours_pandas, EXAMPLE_DATA_SECONDS),
        (expand_to_3_hours, EXAMPLE_DATA_MINUTES),
        (expand_to_3_hours_pandas, EXAMPLE_DATA_MINUTES),
    ],
)
def test_expand_to_3_hours_custom_hours(fnc: Callable, in_data: List[Tuple[int, float]]) -> None:
    # Call the function with a custom duration (1 hour)
    result = fnc(in_data, hours=1)

    # Assert that the result is a list of tuples
    assert isinstance(result, list)
    assert all(isinstance(item, tuple) and len(item) == 2 for item in result)

    timestamps = [item[0] for item in result]
    assert len(timestamps) == len(set(timestamps))  # Check for duplicates

    times = 0
    for x in range(len(result)):
        if x > 0:
            assert result[x - 1][0] == result[x][0] - 1
            times += 1
    assert x > 0
    assert times == len(timestamps) - 1

    assert timestamps[-1] - timestamps[0] == (60 * 60)  # 1 hour in seconds


@pytest.mark.parametrize('fnc', [expand_to_3_hours, expand_to_3_hours_pandas])
def test_expand_to_3_hours_empty_input(
    fnc: Callable,
) -> None:
    result = fnc([])
    assert result == []
