"""
lstpressure.lst.LST
"""
import pandas as pd
from pandas import DataFrame
from datetime import datetime
from typing import Optional, Callable
from ..observation import Observation
from ..observable import Observable
from .helpers import calculate_observations, calculate_observables
from collections import defaultdict
from io import StringIO
from perf import track_total_runtime, decorate_all
from conf import Conf, LogLevel, LocationProviderType
from logger import info, warn

conf = Conf()


@decorate_all(track_total_runtime)
class LST:
    """
    Wrap the LSTCalendar/Observation API for use with SARAO OPT
    CSV downloads.

    Parameters
    ----------
    input : DataFrame | str | list[list[str]]
        The input data source, which can be a DataFrame, a file path to a CSV file, or a list of lists (rows).
    input_filter : Optional[Callable[[list[list[str]]], bool]]
        A filter function to apply to the input data during instantiation. Defaults to None.
    observation_filter : Optional[Callable[[list[Observation]], bool]]
        A filter function to apply to the observations data after filtering the input data. Defaults to None.
    calendar_start : Optional[str | datetime]
        The start date for the LST calendar. Defaults to the current date.
    calendar_end : Optional[str | datetime]
        The end date for the LST calendar. Defaults to the value of calendar_start.

    Attributes
    ----------
    df : DataFrame
        The filtered DataFrame based on the input data and filters.
    input : str | list[list[str]]
        The input data source, which can be a file path to a CSV file, a DataFrame, or a list of lists (rows).
    calendar_start : str | datetime
        The start date for the LST calendar.
    calendar_end : str | datetime
        The end date for the LST calendar.
    observation_filter : Callable[[list[Observation]], bool]
        The filter function applied to the observations data.
    observations : list[Observation]
        A list of Observation objects based on the filtered data.
    observables : list[Observable]
        A list of Observable objects calculated based on the observations.

    Methods
    -------
    write_to_csv(output: str) -> None:
        Write the observables data to a CSV file.

    """

    def __init__(
        self,
        input: DataFrame | str | list[list[str]],
        input_filter: Optional[Callable[[list[str]], bool]] = None,
        observation_filter: Optional[Callable[[Observation], bool]] = None,
        calendar_start: Optional[str | datetime] = None,
        calendar_end: Optional[str | datetime] = None,
        latitude: Optional[str | float] = conf.LATITUDE,
        longitude: Optional[str | float] = conf.LONGITUDE,
        provider: Optional[LocationProviderType] = None,
    ) -> None:
        """
        Initialize an LST object.

        Parameters
        ----------
        input : DataFrame | str | list[list[str]]
            The input data source, which can be a DataFrame, a file path to a CSV file, or a list of lists (rows).
        input_filter : Optional[Callable[[list[str]], bool]]
            A filter function to apply to the input data during instantiation. Defaults to None.
        observation_filter : Optional[Callable[[Observation], bool]]
            A filter function to apply to the observations data after filtering the input data. Defaults to None.
        calendar_start : Optional[str | datetime]
            The start date for the LST calendar. Defaults to the current date.
        calendar_end : Optional[str | datetime]
            The end date for the LST calendar. Defaults to the value of calendar_start.
        latitude : Optional[str | float]
            Latitude for the location. Defaults to -30:42:39.8 (for ASTRAL provider).
        longitude : Optional[str | float]
            Longitude for the location. Defaults to 21:26:38.0 (for ASTRAL provider).

        Raises
        ------
        TypeError
            If the input is not a valid type (DataFrame, str, or list of lists).
        """
        self._input = input
        self._calendar_start = (
            calendar_start if calendar_start else datetime.now().strftime("%Y%m%d")
        )
        self._calendar_end = calendar_end or calendar_start

        self._latitude = latitude
        self._longitude = longitude
        self._provider = provider

        if input_filter and observation_filter:
            warn(
                "Both 'input_filter' and 'observation_filter' are set. Be aware that 'input_filter' "
                "is applied during instantiation with CSV row data, while 'observation_filter' is applied "
                "afterwards to the already filtered data. Future versions of this API might deprecate "
                "'observation_filter' to streamline data processing.",
                category=UserWarning,
            )

        self._observation_filter = (
            observation_filter if observation_filter else lambda _: True
        )
        input_filter = input_filter if input_filter else lambda _: True

        # Process input based on its type
        if isinstance(input, str):
            # Input is a file path, read CSV and filter rows
            df = pd.read_csv(input)
        elif isinstance(input, list):
            # Input is a list of lists, the first list is treated as header
            header, *data = input
            df = pd.DataFrame(data, columns=header)
        elif isinstance(input, DataFrame):
            # Input is already a DataFrame, make a copy
            df = input.copy()
        else:
            raise TypeError(
                "Input must be a path to a CSV file, a DataFrame, or a list of lists (rows)."
            )

        # Apply the filter to the DataFrame
        self._df = df[df.apply(input_filter, axis=1)]

    @property
    def provider(self) -> LocationProviderType:
        return self._provider

    @property
    def df(self) -> DataFrame:
        """
        The filtered DataFrame based on the input data and filters.

        Returns
        -------
        DataFrame
            The filtered DataFrame.
        """
        return self._df

    @property
    def input(self) -> str | list[list[str]]:
        """
        The input data source, which can be a file path to a CSV file, a DataFrame, or a list of lists (rows).

        Returns
        -------
        str | list[list[str]]
            The input data source.
        """
        return self._input

    @property
    def calendar_start(self) -> str | datetime:
        """
        The start date for the LST calendar.

        Returns
        -------
        str | datetime
            The start date.
        """
        return self._calendar_start

    @property
    def calendar_end(self):
        """
        The end date for the LST calendar.

        Returns
        -------
        str | datetime
            The end date.
        """
        return self._calendar_end

    @property
    def observation_filter(self) -> Callable[[list[Observation]], bool]:
        """
        The filter function applied to the observations data.

        Returns
        -------
        Callable[[list[Observation]], bool]
            The observation filter function.
        """
        return self._observation_filter

    @property
    def latitude(self) -> str | float:
        return self._latitude

    @property
    def longitude(self) -> str | float:
        return self._longitude

    @property
    def observations(self) -> list[Observation]:
        """
        A list of Observation objects based on the filtered data.

        Returns
        -------
        list[Observation]
            A list of Observation objects.
        """
        return calculate_observations(self.df, self.observation_filter)

    @property
    def observables(self) -> list[Observable]:
        """
        A list of Observable objects calculated based on the observations.

        Returns
        -------
        list[Observable]
            A list of Observable objects.
        """
        return calculate_observables(
            self.calendar_start,
            self.calendar_end,
            self.observations,
            self.latitude,
            self.longitude,
            provider=self.provider,
        )

    def to_csv(self) -> DataFrame:
        if conf.LOG_LEVEL != LogLevel.WARN:
            info("Creating CSV...")

        data = [o.to_tuple() for o in self.observables]

        # Use a defaultdict to group data by date
        grouped_data = defaultdict(list)
        for record in data:
            (
                id,
                proposal_id,
                date,
                constraint,
                duration,
                lst_window_start,
                lst_window_end,
                lst_interval_start,
                lst_interval_end,
                utc_interval_start,
                utc_interval_end,
            ) = record
            grouped_data[date].append(
                [
                    id,
                    proposal_id,
                    constraint,
                    duration,
                    lst_window_start,
                    lst_window_end,
                    lst_interval_start,
                    lst_interval_end,
                    utc_interval_start,
                    utc_interval_end,
                ]
            )

        # Create a list of dictionaries to construct the DataFrame
        data_list = [
            {
                "Date": date,
                "Observation ID": id,
                "Proposal ID": proposal_id,
                "Interval name": constraint,
                "Duration": duration,
                "Observation window start (LST)": lst_window_start,
                "Observation window end (LST)": lst_window_end,
                "Interval start (LST)": lst_interval_start,
                "Interval end (LST)": lst_interval_end,
                "Interval start (UTC)": utc_interval_start,
                "Interval end (UTC)": utc_interval_end,
            }
            for date, id_value in grouped_data.items()
            for id, proposal_id, constraint, duration, lst_window_start, lst_window_end, lst_interval_start, lst_interval_end, utc_interval_start, utc_interval_end in id_value
        ]

        # Construct the DataFrame
        df = pd.DataFrame(data_list)
        return df

    def to_csv_buffer(self) -> StringIO:
        df = self.to_csv()
        buffer = StringIO()
        df.to_csv(
            buffer, sep=",", quotechar='"', quoting=1, index=False, encoding="utf-8"
        )
        return buffer

    def to_csv_string(self) -> str:
        return self.to_csv_buffer().getvalue()

    def to_csv_file(self, output: str) -> None:
        df = self.to_csv()
        df.to_csv(
            output, sep=",", quotechar='"', quoting=1, index=False, encoding="utf-8"
        )
