import pytest
from lstpressure import LSTCalendar, LSTIntervalType as I
from lstpressure.observation import Observation

OBSERVATIONS = [
    Observation(
        o.get("id"),
        o.get("lst_window_start"),
        o.get("lst_window_end"),
        o.get("utc_constraints"),
        o.get("duration"),
    )
    for o in [
        {
            "id": "O1",
            "lst_window_start": 6.5,
            "lst_window_end": 10.2,
            "utc_constraints": [I.ALL_DAY],
            "duration": 1,
        },
        {
            "id": "O2",
            "lst_window_start": 8.5,
            "lst_window_end": 10.2,
            "utc_constraints": [I.NIGHT],
            "duration": 1,
        },
        {
            "id": "O3",
            "lst_window_start": 21.5,
            "lst_window_end": 20,
            "utc_constraints": [I.NIGHT],
            "duration": 0.5,
        },
        {
            "id": "O4",
            "lst_window_start": 12,
            "lst_window_end": 22,
            "utc_constraints": [I.NIGHT],
            "duration": 1.5,
        },
        {
            "id": "O5",
            "lst_window_start": 9,
            "lst_window_end": 10,
            "utc_constraints": [I.SUNRISE_SUNSET],
            "duration": 0.5,
        },
    ]
]


@pytest.mark.parametrize(
    "start, end, expected",
    [
        ("20230404", "20230404", ["20230404"]),
        ("20230404", "20230405", ["20230404", "20230405"]),
        ("20220101", "20220105", ["20220101", "20220102", "20220103", "20220104", "20220105"]),
        (
            "20231025",
            "20231031",
            ["20231025", "20231026", "20231027", "20231028", "20231029", "20231030", "20231031"],
        ),
    ],
)
def test_Calendar(start, end, expected):
    """
    The calendar should convert start/end params into the correct range
    """
    assert expected == [d.dt.strftime("%Y%m%d") for d in LSTCalendar(start, end)._dates]


# Invalid start/end should NOT work
@pytest.mark.parametrize(
    "start, end",
    [("invalidStart", "20220105"), ("20220101", "invalidEnd"), ("20220105", "20220101")],
)
def test_calendar_raises_exception_for_invalid_dates(start, end):
    with pytest.raises(ValueError):
        LSTCalendar(start, end)


# The observations property should return all the observations
@pytest.mark.parametrize(
    "dt_range", [(["20231101"]), (["20231101", "20231101"]), (["20231101", "20231201"])]
)
def test_self_observations(dt_range):
    start = dt_range[0]
    end = dt_range[1] if len(dt_range) == 2 else start
    calendar = LSTCalendar(start, end, observations=OBSERVATIONS)
    assert len(calendar.observations) == len(OBSERVATIONS)
