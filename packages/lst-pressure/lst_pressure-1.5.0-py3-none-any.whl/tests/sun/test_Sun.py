import pytest
from lstpressure.sun import Sun
from lstpressure.sun.location_providers import MeerKATProvider
from lstpressure.sun.location_providers.normalize_intervals import normalize_interval
from lstpressure.sun.location_providers.astral_provider.AstralProvider import (
    normalize_interval,
    AstralProvider,
)
from conf import Conf, LocationProviderType
from lstpressure.utils import normalize_yyyymmdd_to_datetime

conf = Conf()
conf.LOC_PROVIDER = LocationProviderType.ASTRAL

latitude, longitude = ["-30:42:39.8", "21:26:38.0"]

# NOTE - all times are in UTC unless suffixed with "_lst"

data = [
    (
        "20231204",
        {
            "meerkat_provider": {
                "dawn": None,
                "sunrise": "2023-12-04 03:27:00.000000",
                "sunrise_lst": 9.74,
                "noon": None,
                "sunset": "2023-12-04 17:17:00.000000",
                "sunset_lst": 23.6,
                "dusk": None,
            },
        },
    ),
    (
        "20231121",
        {
            "astral_provider": {
                "dawn": "2023-11-21 02:59:16.055392",
                "sunrise": "2023-11-21 03:26:25.080197",
                "noon": "2023-11-21 10:19:52.000000",
                "sunset": "2023-11-21 17:13:54.229446",
                "dusk": "2023-11-21 17:41:06.904472",
            },
            "meerkat_provider": {
                "dawn": None,
                "sunrise": "2023-11-21 03:29:00.000000",
                "noon": None,
                "sunset": "2023-11-21 17:06:00.000000",
                "dusk": None,
            },
        },
    ),
    (
        "20230615",
        {
            "astral_provider": {
                "dawn": "2023-06-15 05:02:41.873453",
                "sunrise": "2023-06-15 05:29:46.909659",
                "noon": "2023-06-15 10:34:34.000000",
                "sunset": "2023-06-15 15:39:30.356171",
                "dusk": "2023-06-15 16:06:35.427817",
            },
            "meerkat_provider": {
                "dawn": None,
                "sunrise": "2023-06-15 05:32:00.000000",
                "noon": None,
                "sunset": "2023-06-15 15:32:00.000000",
                "dusk": None,
            },
        },
    ),
]


@pytest.mark.parametrize(
    "yyyymmdd, expected_results",
    data,
)
def test_Sun_with_AstralProvider(yyyymmdd, expected_results):
    if expected_results.get('"astral_provider"'):
        sun = Sun(yyyymmdd, latitude, longitude)
        for event, expected_time in expected_results["astral_provider"].items():
            calculated_time = getattr(sun, event).strftime("%Y-%m-%d %H:%M:%S.%f")
            assert calculated_time == expected_time


@pytest.mark.parametrize(
    "yyyymmdd, expected_results",
    data,
)
def test_Sun_with_MeerKATProvider(yyyymmdd, expected_results):
    sun = Sun(yyyymmdd=yyyymmdd, provider=LocationProviderType.MEERKAT)

    for event, expected_time in expected_results["meerkat_provider"].items():
        try:
            calculated_time = getattr(sun, event)
            if isinstance(calculated_time, float):
                assert expected_time == round(calculated_time, 2)
            else:
                assert expected_time == calculated_time.strftime("%Y-%m-%d %H:%M:%S.%f")

        except AttributeError:
            calculated_time = None


@pytest.mark.parametrize(
    "start, end, expected",
    [
        (7, 13, (7, 13)),
        (22, 7, (22, 31)),
        (1, 6, (1, 6)),
        (18, 2, (18, 26)),
    ],
)
def test_normalize_interval(start, end, expected):
    result = normalize_interval(start, end)
    assert result == expected


@pytest.mark.parametrize(
    "latitude,longitude,today_dt",
    [
        ("-30:42:39.8", "21:26:38.0", "20231116"),
    ],
)
def test_calculate_intervals(latitude, longitude, today_dt):
    today = normalize_yyyymmdd_to_datetime(today_dt)
    intervals = AstralProvider.calc_intervals(Sun, latitude, longitude, today, None)
    # TODO - what to assert
