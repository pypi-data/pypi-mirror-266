import pytest
from lstpressure.utils import utc_to_lst, normalize_time_to_decimal, normalize_coordinates


@pytest.mark.parametrize("input,expected", [("6:26:20", 6.438888888888889)])
def test_normalize_time_to_decimal(input, expected):
    result = normalize_time_to_decimal(input)
    assert result == expected


# https://www.localsiderealtime.com/


@pytest.mark.parametrize(
    "utc,latitude,longitude,expected",
    [
        ("2023-10-26 09:21:50", "-30:42:39.8", "21:26:38.0", "13:05:36"),
        ("2023-10-26 08:26:20", "-30:42:39.8", "21:26:38.0", 12.165872678174422),
        ("2023-10-26 09:21:50", -30.7111, 21.4439, "13:05:36"),
    ],
)
def test_utc_to_lst(utc, latitude, longitude, expected):
    result = utc_to_lst(utc, *normalize_coordinates(latitude, longitude))
    assert round(normalize_time_to_decimal(result), 2) == round(
        normalize_time_to_decimal(expected), 2
    )
