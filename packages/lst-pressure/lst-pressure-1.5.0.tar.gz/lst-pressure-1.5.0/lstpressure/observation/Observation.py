"""
lstpressure.observation.Observation
"""

from typing import Optional, Tuple
from ..lstcalendar.LSTCalendarDate import LSTCalendar, Observable
from ..lstindex import LSTIntervalType, LSTInterval, normalize_interval
from perf import track_total_runtime, decorate_all


@decorate_all(track_total_runtime)
class Observation:
    """
    Represents an observation block with given Local Sidereal Time (LST) window and UTC constraints.

    Attributes
    ----------
    id: any
        The ID of the observation block
    lst_window_start : float
        The starting value of the LST window.
    lst_window_end : float
        The ending value of the LST window.
    utc_constraints : list[LSTInterval]
        The UTC constraints for the observation block represented as a list of LSTInterval values. Defaults to 0.
    """

    def __init__(
        self,
        id: any,
        lst_window_start: float,
        lst_window_end: float,
        utc_constraints: LSTIntervalType | list[LSTIntervalType] = None,
        duration: float = None,
        proposal_id: str = None,
    ) -> None:
        """
        Initializes an instance of Block.

        Parameters
        ----------
        id: any
            The ID of the observation block
        lst_window_start : float
            The starting value of the LST window.
        lst_window_end : float
            The ending value of the LST window.
        utc_constraints : list[LSTInterval]
            The UTC constraints for the observation block represented as a list of LSTInterval values. Defaults to 0.
        """
        self.id = id
        self.lst_window_start = lst_window_start
        self.lst_window_end = lst_window_end
        self.utc_constraints = (
            utc_constraints
            if utc_constraints and isinstance(utc_constraints, list)
            else [utc_constraints]
        )
        self.proposal_id = proposal_id
        self._duration = duration if duration else 0
        self._cal: Optional[LSTCalendar] = None  # Reference to the calendar
        self._intervals = []
        self._intervals.append(
            LSTInterval(
                *normalize_interval(self.lst_window_start, self.lst_window_end),
                None,
                None,
                parent=self,
                type=LSTIntervalType.OBSERVATION_WINDOW,
            )
        )
        if self.lst_window_end < self.lst_window_start:
            self._intervals.append(
                LSTInterval(0, self.lst_window_end, None, None, self)
            )

    @property
    def duration(self) -> float:
        """
        Required observation duration in hours (decimal)
        """
        return self._duration

    @property
    def intervals(self) -> list[LSTInterval]:
        return self._intervals

    @property
    def calendar(self) -> LSTCalendar:
        if not self._cal:
            raise ValueError("Block has not been added to any LSTCalendar.")
        return self._cal

    @calendar.setter
    def calendar(self, cal: LSTCalendar):
        self._cal = cal

    def __hash__(self) -> int:
        return hash((self.id, self.lst_window_start, self.lst_window_end))

    def observables(
        self, lstcalendar: Optional[LSTCalendar] = None
    ) -> Tuple[Observable]:
        lstcalendar = self._cal if not lstcalendar else lstcalendar

        if not lstcalendar:
            raise ValueError(
                "'lstcalendar' is not specified. To check observability, either associate this observation with an existing LSTCalendar instance or pass an LSTCalendar instance as an argument to this method."
            )

        results = set()

        # Note that overlap() returns a set
        query_result = set()
        for obs_window in self.intervals:
            query_result = query_result | lstcalendar.interval_index.overlap(
                obs_window.interval
            )

            for cal_interval_raw in query_result:
                cal_interval_start, cal_interval_end, cal_interval = cal_interval_raw
                interval_type = cal_interval.type

                if (self.utc_constraints is None or len(self.utc_constraints) == 0) or (
                    len(self.utc_constraints) > 0
                    and interval_type in self.utc_constraints
                ):
                    if obs_window.end > cal_interval_start:
                        if (
                            obs_window.start + self.duration < cal_interval_end
                            or obs_window.end + self.duration < cal_interval_end
                        ):
                            results.add(Observable(cal_interval, self))

        return tuple(results)
