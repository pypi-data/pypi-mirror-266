"""
lstpressure.lstcalendar.LSTCalendar
"""
from datetime import timedelta, datetime
from typing import Dict, Optional, Self
from ..observation import Observation
from ..observable import Observable
from .LSTCalendarDate import LSTCalendarDate
from ..lstindex import LSTIndex, LSTInterval
from ..utils import (
    normalize_yyyymmdd_to_datetime,
    normalize_coordinates,
)
from perf import decorate_all, track_total_runtime
from logger import info
from conf import Conf, LocationProviderType

conf = Conf()


@decorate_all(track_total_runtime)
class LSTCalendar:
    """
    Calendar tailored for LST (Local Sidereal Time) related interval lookups.

    Attributes
    ----------
    start : str | datetime
        The beginning of the date range for the calendar.
    end : Optional[str | datetime]
        The conclusion of the date range for the calendar. Defaults to None.
    latitude : float
        The geographic latitude in decimal degrees. Defaults to 0.
    longitude : float
        The geographic longitude in decimal degrees. Defaults to 0.
    interval_index : LSTIndex
        An index to manage intervals efficiently.
    observations_index : LSTIndex
        An index to manage observations efficiently.
    dates : list[LSTCalendarDate]
        A list containing dates and corresponding sun statistics within the range.

    Methods
    -------
    __init__(start, end, latitude=0, longitude=0, observations=[])
        Initialize the LSTCalendar object.
    __enter__()
        Enter context management.
    __exit__(exc_type, exc_val, exc_tb)
        Exit context management.
    load_observations(observations: list[Observation]) -> LSTCalendar
        Load a list of observations and insert their intervals into the observation index.
    observables(observations: Optional[list[Observation]] = None) -> list[Observable]
        Retrieve observable observations for the dates maintained by this calendar.

    """

    def __enter__(self):
        """
        Enter context management.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context management.
        """
        pass

    def __init__(
        self,
        start: str | datetime,
        end: Optional[str | datetime] = None,
        observations: list[Observation] = [],
        latitude: Optional[str | float] = conf.LATITUDE,
        longitude: Optional[str | float] = conf.LONGITUDE,
        provider: Optional[LocationProviderType] = None,
    ):
        """
        Initialize the LSTCalendar object.

        Parameters
        ----------
        start : str | datetime
            Start date of the calendar range.
        end : (Optional) str | datetime
            End date of the calendar range. Defaults to start.
        observations : list[Observation], optional
            list of observation instances. Called load_observations method under the hood.
        latitude : str | float, optional
            Latitude for the location. Defaults to -30:42:39.8 (for ASTRAL provider).
        longitude : str | float, optional
            Longitude for the location. Defaults to 21:26:38.0 (for ASTRAL provider).

        Raises
        ------
        ValueError
            If the start date is after the end date.
        """
        info(f"Initializing calendar ({conf.LOC_PROVIDER.name} location provider)...")
        start = normalize_yyyymmdd_to_datetime(start)
        end = start if not end else normalize_yyyymmdd_to_datetime(end)

        if start > end:
            raise ValueError("start day should be <= end day")

        if latitude and longitude:
            latitude, longitude = normalize_coordinates(latitude, longitude)
        self.latitude = latitude
        self.longitude = longitude
        self._interval_index = LSTIndex()
        self._observations_index = LSTIndex()
        self._dates = [
            LSTCalendarDate(start + timedelta(days=d), self, provider=provider)
            for d in range(0, (end - start).days + 1)
        ]
        self.load_observations(observations)

    @property
    def interval_index(self) -> LSTIndex:
        """
        Property to retrieve the interval index.

        Returns
        -------
        LSTIndex
            An index to manage intervals efficiently.
        """
        return self._interval_index

    @property
    def observations_index(self) -> LSTIndex:
        """
        Property to retrieve the observations index.

        Returns
        -------
        LSTIndex
            An index to manage observations efficiently.
        """
        return self._observations_index

    @property
    def dates(self) -> list[LSTCalendarDate]:
        """
        Property to retrieve the list of dates.

        Returns
        -------
        list[LSTCalendarDate]
            A list containing dates and corresponding sun statistics within the range.
        """
        return self._dates

    def load_observations(self, observations: list[Observation]) -> Self:
        """
        Load a list of observations, set the calendar attribute for each observation,
        and insert their intervals into the observation index.

        Observations must have unique IDs.

        Parameters
        ----------
        observations : list[Observation]
            A list of observation instances.

        Returns
        -------
        LSTCalendar
            The LSTCalendar object.
        """
        self._observations = []
        self._observations_index = LSTIndex()
        _primary_keys = set()
        for observation in observations:
            # Create a composite key using both id and utc_constraints
            composite_key = (
                observation.id,
                "".join([c.name for c in observation.utc_constraints]),
            )

            # Check if the composite key is already in the set
            if composite_key in _primary_keys:
                raise ValueError(
                    f"Duplicate composite key detected: ID '{observation.id}' with UTC constraints '{observation.utc_constraints}'. "
                    "Each observation must have a unique combination of ID and UTC constraints to be loaded into the calendar."
                )

            # Add the composite key to the set for future checks
            _primary_keys.add(composite_key)

            # Assign the calendar to the observation and append it to the calendar's list of observations
            observation.calendar = self
            self._observations.append(observation)

            # Insert intervals from the observation into the calendar's observation index
            for interval in observation.intervals:
                self.observations_index.insert(interval.interval)
        return self

    @property
    def observations(self) -> list[Dict[str, LSTInterval | Observation]]:
        """
        Property to retrieve the list of observations.

        Returns
        -------
        list[Dict[str, LSTInterval | Observation]]
            A list of observations.
        """
        return self._observations

    @observations.setter
    def observations(self, observations: list[Observation]) -> None:
        """
        Setter for the observations property. It serves as an alias for the load_observations method.

        Parameters
        ----------
        observations : list[Observation]
            A list of observation instances.

        Returns
        -------
        None
        """
        self.load_observations(observations)

    def observables(
        self, observations: Optional[list[Observation]] = None
    ) -> list[Observable]:
        """
        Retrieve observable observations for the dates maintained by this calendar.

        This method processes a list of dates within the calendar and aggregates their observable observations into observation windows. If a list of observations is provided, it replaces the current observations of the calendar with the new list.

        Parameters
        ----------
        observations : Optional[list[Observation]], optional
            A list of Observation objects to process, which is optional. If provided, it overwrites any existing observations in the calendar.

        Raises
        ------
        TypeError
            If no observations have been loaded into the calendar and none are provided.

        Returns
        -------
        list[Observable]
            A list of aggregated observation windows, each representing observable observations for a specific date in the calendar.

        Example usage:

        .. code-block:: python

            calendar = Calendar()
            calendar.load_dates(dates)
            try:
                observation_windows = calendar.observable_observations()
            except TypeError as e:
                print(e)

        """
        # If observations provided as an argument, assume the intent is to overwrite
        if observations:
            self.load_observations(observations)

        if not self.observations:
            raise TypeError(
                "No observations have been loaded on this calendar, and no observations have been provided as an argument"
            )

        results = []
        for dt in self.dates:
            results = results + dt.observables()

        return results
