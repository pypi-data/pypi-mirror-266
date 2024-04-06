"""
lstpressure.lstindex.LSTIntervalType
"""

from enum import Enum, auto


class LSTIntervalType(Enum):
    """
    Enumeration of LST (Local Sidereal Time) interval types.

    Defines various types of LST intervals that can be associated with observations or calendar events.

    Attributes
    ----------
    ALL_DAY : LSTIntervalType
        An interval type representing a full day, spanning from 0 to 24 hours.
    NIGHT : LSTIntervalType
        An interval type representing the nighttime period.
    OBSERVATION_WINDOW : LSTIntervalType
        An interval type representing an observation window.
    SUNRISE_SUNSET : LSTIntervalType
        An interval type representing the period from sunrise to sunset.
    SUNSET_SUNRISE : LSTIntervalType
        An interval type representing the period from sunset to sunrise.
    """

    ALL_DAY = auto()
    NIGHT = auto()
    OBSERVATION_WINDOW = auto()
    SUNRISE_SUNSET = auto()
    SUNSET_SUNRISE = auto()
