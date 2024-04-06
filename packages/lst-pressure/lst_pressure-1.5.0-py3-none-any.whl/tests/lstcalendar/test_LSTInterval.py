import pytest
from lstpressure.lstindex import LSTInterval, LSTIntervalType
from intervaltree import Interval
from datetime import datetime


@pytest.mark.parametrize(
    "start, end, dt, interval_type",
    [
        (
            1,
            2,
            "20230219",
            LSTIntervalType.NIGHT,
        ),
        (
            1,
            2,
            "20230219",
            None,
        ),
    ],
)
def test_LSTInterval(start, end, dt, interval_type):
    interval = LSTInterval(start, end, None, None, None, dt, interval_type)
    _interval = interval.interval
    assert isinstance(_interval, Interval)
    assert isinstance(_interval[2], LSTInterval)
    assert interval.start == _interval[0]
    assert interval.end == _interval[1]
    assert interval.type == interval_type
    assert interval.dt == datetime.strptime(dt, "%Y%m%d").date()
