import pytest
from datetime import datetime, date
from lstpressure.utils import normalize_datetime, normalize_yyyymmdd_to_datetime


@pytest.mark.parametrize(
    "input,expected", [("2023-12-20 00:00:00", datetime(2023, 12, 20, 0, 0, 0))]
)
def test_normalize_datetime(input, expected):
    result = normalize_datetime(input)
    assert result == expected


@pytest.mark.parametrize("input,expected", [("20230222", date(2023, 2, 22))])
def test_normalize_yyyymmdd_to_datetime(input, expected):
    result = normalize_yyyymmdd_to_datetime(input)
    assert result == expected
