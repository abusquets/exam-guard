import pytest

from fixtures.generate_data import nine_minutes_heart_rate

from utils.dataframe import expand_to_3_hours, extract_outliers


@pytest.mark.asyncio
class TestMonitorAlertUseCase:
    def test_extract_suspicious_data(self) -> None:
        example = nine_minutes_heart_rate()
        data = expand_to_3_hours(example, hours=1)
        start_value = data[0][1]
        threshold = 30
        threshold_value = start_value + (start_value * threshold / 100)
        interval = 90
        pos = 0
        for i in range(len(data)):
            if data[i][1] > threshold_value:
                pos = i
                break
        data = data[pos:][:interval]

        # Act
        res = extract_outliers(start_value, data, threshold, interval)

        # Expect
        assert res
