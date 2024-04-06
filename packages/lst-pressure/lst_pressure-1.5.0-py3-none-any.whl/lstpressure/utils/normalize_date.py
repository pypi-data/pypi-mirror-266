"""
normalize_date.py
"""
from functools import lru_cache
from datetime import date, datetime
from perf import track_total_runtime


@track_total_runtime
@lru_cache(maxsize=None)
def normalize_yyyymmdd_to_datetime(yyyymmdd) -> date:
    """
    normalize_date
    In many cases it's useful to create a date from a yyyymmdd string
    This helper function is to allow inputting either a string or date
    object and getting back a date object at 00:00 of that day
    """
    if isinstance(yyyymmdd, str):
        year, month, day = int(yyyymmdd[:4]), int(yyyymmdd[4:6]), int(yyyymmdd[6:])
    else:
        year, month, day = yyyymmdd.year, yyyymmdd.month, yyyymmdd.day
    return date(year, month, day)


@track_total_runtime
@lru_cache(maxsize=None)
def normalize_datetime(dt_input) -> datetime:
    """
    normalize_datetime
    Normalizes a datetime object (either a string or a date) to a datetime object

    dt_input("2023-12-20 00:00:00"): <class 'datetime.datetime'> 2023-12-30 00:00:00
    dt_input(datetime(2023, 12, 20, 0, 0, 0)): <class 'datetime.datetime'> 2023-12-30 00:00:00
    """
    if isinstance(dt_input, str):
        return datetime.fromisoformat(dt_input)
    return dt_input
