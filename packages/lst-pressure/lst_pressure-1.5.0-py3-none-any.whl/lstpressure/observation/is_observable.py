from ..lstcalendar import LSTCalendar
from .Observation import Observation
from typing import Optional
from perf import track_total_runtime
from conf import Conf, LocationProviderType

conf = Conf()


@track_total_runtime
def is_observable(
    observation: Observation,
    yyyymmdd_start: Optional[str] = None,
    yyyymmdd_end: Optional[str] = None,
    lstCalendar: Optional[LSTCalendar] = None,
    latitude: Optional[str | float] = conf.LATITUDE,
    longitude: Optional[str | float] = conf.LONGITUDE,
    provider: Optional[LocationProviderType] = None,
) -> bool:
    """
    Determines if an Observation is observable within the specified date and location parameters.

    Parameters
    ----------
    observation : Observation
        The Observation object to be checked.
    yyyymmdd_start : str, optional
        (Optional) The start date in the format 'YYYYMMDD'.
    yyyymmdd_end : str, optional
        (Optional) The end date in the format 'YYYYMMDD'. If not provided, the start date is used.
    lstCalendar : LSTCalendar, optional
        (Optional) An instance of LSTCalendar. If not provided, a new LSTCalendar instance will be created based on the date and location parameters.
    latitude : str or float, optional
        (Optional) The latitude for the observation in the format 'D:M:S'. Defaults to -30:42:39.8 (for ASTRAL provider).
    longitude : str or float, optional
        (Optional) The longitude for the observation in the format 'D:M:S'. Defaults to 21:26:38.0 (for ASTRAL provider).

    Returns
    -------
    bool
        True if the observation is observable within the specified parameters, False otherwise.
    """

    # TODO fix me. Some import problem
    from ..lstcalendar import LSTCalendar

    yyyymmdd_end = yyyymmdd_end if yyyymmdd_end else yyyymmdd_start

    # Create an LSTCalendar instance if not provided
    calendar = (
        lstCalendar
        if lstCalendar
        else LSTCalendar(
            yyyymmdd_start, yyyymmdd_end, latitude=latitude, longitude=longitude, provider=provider
        )
    )

    return bool(observation.observables(calendar))
