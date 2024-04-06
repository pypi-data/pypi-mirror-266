"""
observable.Observable
"""
from datetime import datetime
from typing import Any, Self
from ..observation import Observation
from ..lstindex import LSTInterval, LSTIntervalType
from perf import track_total_runtime, decorate_all


@decorate_all(track_total_runtime)
class Observable:
    """
    Represents a valid scheduling time frame based on observational constraints.

    Attributes:
        interval (LSTInterval): The time interval or range representing the observation window.
        observation (Observation): The observational data or constraints defining the validity of the interval.

    Args:
        interval (LSTInterval): The time interval or range for the observation window.
        observation (Observation): The observational constraints or data associated with the interval.
    """

    def __init__(self, interval: LSTInterval, observation: Observation):
        """
        Initializes an instance of the Observable class.

        Args:
            interval (LSTInterval): The time interval or range for the observation window.
            observation (Observation): The observational constraints or data associated with the interval.
        """
        self._interval = interval
        self._observation = observation

    @property
    def interval(self) -> LSTInterval:
        """
        Returns the time interval or range representing the observation window.

        Returns:
            LSTInterval: The time interval or range for the observation.
        """
        return self._interval

    @property
    def observation(self) -> Observation:
        """
        Returns the observational data or constraints defining the validity of the interval.

        Returns:
            Observation: The observational constraints or data.
        """
        return self._observation

    @property
    def id(self) -> Any:
        """
        Returns the identification of the observation.

        Returns:
            Any: The identification of the observation.
        """
        return self.observation.id

    @property
    def proposal_id(self) -> Any:
        """
        Returns the proposal identification associated with the observation.

        Returns:
            Any: The proposal identification.
        """
        return self.observation.proposal_id

    @property
    def dt(self) -> datetime:
        """
        Returns the date and time of the observation.

        Returns:
            datetime: The date and time of the observation.
        """
        return self.interval.dt

    @property
    def duration(self) -> float:
        """
        Returns the duration of the observation.

        Returns:
            float: The duration of the observation in hours.
        """
        return self.observation.duration

    @property
    def utc_constraint(self) -> LSTIntervalType:
        """
        Returns the UTC constraint type of the observation interval.

        Returns:
            LSTIntervalType: The UTC constraint type of the interval.
        """
        return self.interval.type.name

    def to_tuple(self):
        """
        Converts the Observable instance into a tuple representation.

        This method is useful for serializing the object for storage or transmission.

        Returns:
            Tuple: A tuple containing the essential attributes of the Observable instance.
        """
        lst_window_end = self.interval.end
        if lst_window_end > 24:
            lst_window_end = lst_window_end - 24

        return (
            self.id,
            self.proposal_id,
            self.dt.strftime("%Y-%m-%d"),
            self.utc_constraint,
            round(self.duration, 2),
            self.observation.lst_window_start,
            self.observation.lst_window_end,
            round(self.interval.start, 2),
            round(lst_window_end, 2),
            self.interval.start_utc,
            self.interval.end_utc,
        )

    def __lt__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return (self.id, self.dt, self.utc_constraint, self.duration, self.interval.start) < (
            other.id,
            other.dt,
            other.utc_constraint,
            other.duration,
            other.interval.start,
        )

    def __le__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return (self.id, self.dt, self.utc_constraint, self.duration, self.interval.start) <= (
            other.id,
            other.dt,
            other.utc_constraint,
            other.duration,
            other.interval.start,
        )

    def __eq__(self, other: Self) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return (
            self.interval.dt,
            self.utc_constraint,
            self.duration,
            self.interval.start,
            self.interval.end,
            self.observation.id,
        ) == (
            other.interval.dt,
            other.utc_constraint,
            other.duration,
            other.interval.start,
            other.interval.end,
            other.observation.id,
        )

    def __ge__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return (self.id, self.dt, self.utc_constraint, self.duration, self.interval.start) >= (
            other.id,
            other.dt,
            other.utc_constraint,
            other.duration,
            other.interval.start,
        )

    def __gt__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return (self.id, self.dt, self.utc_constraint, self.duration, self.interval.start) > (
            other.id,
            other.dt,
            other.utc_constraint,
            other.duration,
            other.interval.start,
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.interval.dt,
                self.utc_constraint,
                self.duration,
                self.interval.start,
                self.interval.end,
                self.observation.id,
            )
        )

    def __str__(self) -> int:
        return f"{self.interval.dt}{self.interval.type}{self.interval.start}{self.interval.end}{self.observation.id}"
