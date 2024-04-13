from fixtures.generate_data import expand_to_3_hours, nine_minutes_heart_rate


def test_expexpand_to_3_hours() -> None:
    example = nine_minutes_heart_rate()
    data = expand_to_3_hours(example, 1)
    to_subtract = len(data) - (9 * 60) * (60 // 9)
    data = data[:-to_subtract]
    start_value = data[0][1]
    threshold = 30
    value_threshold = start_value + (start_value * threshold / 100)
    interval = 90

    itimes = 0
    threshold_data_times = 0
    for j in range(len(data)):
        value = data[j][1]
        if value > value_threshold:
            itimes += 1
        else:
            itimes = 0

        if itimes == interval:
            threshold_data_times += 1

    assert threshold_data_times == 60 // 9
