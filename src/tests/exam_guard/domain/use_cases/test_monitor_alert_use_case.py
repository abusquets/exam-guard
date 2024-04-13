from unittest.mock import Mock

import pytest

from fixtures.generate_data import expand_to_3_hours, nine_minutes_heart_rate

from exam_guard.domain.use_cases.monitor_alert import MonitorAlertUseCase


@pytest.mark.asyncio
class TestMonitorAlertUseCase:
    def test_extract_suspicious_data(self) -> None:
        # Prepare
        use_case = MonitorAlertUseCase(Mock(), 30)

        example = nine_minutes_heart_rate()
        data = expand_to_3_hours(example, 1)
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
        res = use_case.extract_suspicious_data(data, start_value, threshold, interval)

        # Expect
        assert res
