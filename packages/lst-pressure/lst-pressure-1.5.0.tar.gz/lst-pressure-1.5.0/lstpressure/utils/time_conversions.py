"""
lstpressure.time_conversions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Module containing time conversion utilities, including conversion from UTC to Local Sidereal Time (LST) 
and conversion from a time string to its decimal hour representation.
"""

from astropy.time import Time
from astropy import units as u, coordinates
from functools import lru_cache
from astropy.utils import iers
from datetime import datetime
from .normalize_coordinates import normalize_coordinates
from .normalize_date import normalize_datetime
from perf import track_total_runtime


# iers.conf.auto_download = False
# iers.conf.auto_max_age = None
# iers.conf.iers_degraded_accuracy = "warn"

# Constants
LST_DAY_DEC = 23.9344696
"""Length of a sidereal day in decimal hours."""


@track_total_runtime
@lru_cache(maxsize=None)
def utc_to_lst(
    iso_date: str | datetime,
    lat: str | float = None,
    long: str | float = None,
    address: str = None,
) -> float:
    """
    Convert a given UTC datetime to Local Sidereal Time (LST).

    Parameters:
    -----------
    iso_date : str | datetime
        An ISO 8601 date string or datetime object representing UTC time.
    lat : str | float
        Latitude coordinate, can be a string (e.g., "52d40m") or float.
    long : str | float
        Longitude coordinate, can be a string (e.g., "4d55m") or float.
    address : str
        Address that is resolved to lat/long (instead of passing lat/long) via OpenStreetMap API

    Returns:
    --------
    float
        The Local Sidereal Time in decimal hours.

    Example:
    --------
    >>> utc_to_lst("2023-10-26T12:00:00", "52d40m", "4d55m")
    14.5567
    """
    if address:
        location = coordinates.EarthLocation.of_address(address)
        longitude = location.lon
        latitude = location.lat
        long = longitude.value
        lat = latitude.value

    lat, long = normalize_coordinates(lat, long)
    location = coordinates.EarthLocation(long, lat)
    t = Time(val=normalize_datetime(iso_date), format="datetime", location=location)
    lst = t.sidereal_time(kind="apparent", model="IAU2006A")
    return lst.to_value()


@track_total_runtime
@lru_cache(maxsize=None)
def normalize_time_to_decimal(time: str | float) -> float:
    """
    Convert a time string of format hours:min:sec to decimal hours.

    Parameters:
    -----------
    time : str
        A time string formatted as "hours:min:sec".

    Returns:
    --------
    float
        The time represented in decimal hours.

    Raises:
    -------
    ValueError
        If the input time is not a string or if it doesn't have the expected format.

    Example:
    --------
    >>> time_to_decimal("2:30:0")
    2.5
    """
    if isinstance(time, float):
        return time

    if not isinstance(time, str):
        raise ValueError("Input should be a string in format hours:min:sec")

    # Split the time string by colon to get hours, minutes, and seconds
    components = time.split(":")

    if len(components) != 3:
        raise ValueError("Time string should have format hours:min:sec")

    hours, minutes, seconds = map(int, components)

    # Convert time components to decimal hours
    decimal_hours = hours + (minutes / 60) + (seconds / 3600)

    return decimal_hours
