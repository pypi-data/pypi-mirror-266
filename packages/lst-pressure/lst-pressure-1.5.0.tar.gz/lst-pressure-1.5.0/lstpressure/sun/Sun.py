"""
lstpressure.sun.Sun
"""
from typing import Optional
from .location_providers import AstralProvider, MeerKATProvider
from ..utils import normalize_coordinates, normalize_yyyymmdd_to_datetime, utc_to_lst
from perf import track_total_runtime, decorate_all
from conf import LocationProviderType as LocationProviderType, Conf

conf = Conf()

provider_mapping = {
    LocationProviderType.ASTRAL: AstralProvider,
    LocationProviderType.MEERKAT: MeerKATProvider,
}


@decorate_all(track_total_runtime)
class Sun:
    """
    Sun statistics for a particular date, at a particular lat/long.

    Attributes
    ----------
    dawn : datetime
        The dawn time for the given date and location.
    dawn_lst : datetime
        The dawn time converted to Local Sidereal Time (LST) for the given date and location.
    sunrise : datetime
        The sunrise time for the given date and location.
    sunrise_lst : datetime
        The sunrise time converted to Local Sidereal Time (LST) for the given date and location.
    noon : datetime
        The solar noon time for the given date and location.
    noon_lst : datetime
        The solar noon time converted to Local Sidereal Time (LST) for the given date and location.
    sunset : datetime
        The sunset time for the given date and location.
    sunset_lst : datetime
        The sunset time converted to Local Sidereal Time (LST) for the given date and location.
    dusk : datetime
        The dusk time for the given date and location.
    dusk_lst : datetime
        The dusk time converted to Local Sidereal Time (LST) for the given date and location.

    Parameters
    ----------
    latitude : float | str
        The latitude of the location in decimal degrees or string format.
    longitude : float | str
        The longitude of the location in decimal degrees or string format.
    yyyymmdd : str
        The date in 'YYYYMMDD' format for which sun statistics are calculated.

    Raises
    ------
    ValueError
        If the date format is incorrect or if the location coordinates cannot be normalized.

    """

    def __init__(
        self,
        yyyymmdd: str,
        latitude: Optional[float | str] = None,
        longitude: Optional[float | str] = None,
        provider: Optional[LocationProviderType] = conf.LOC_PROVIDER,
    ) -> None:
        """
        Initialize a Sun object.

        Parameters
        ----------
        yyyymmdd : str
            The date in 'YYYYMMDD' format for which sun statistics are calculated.
        latitude : Optional[float | str]
            The latitude of the location in decimal degrees or string format. Defaults to None.
        longitude : Optional[float | str]
            The longitude of the location in decimal degrees or string format. Defaults to None.
        provider: Optional[LocationProviderType]
            A sun/time provider for customizing class calculations. Defaults to LocationProviderType.ASTRAL.

        Raises
        ------
        ValueError
            If the date format is incorrect or if the location coordinates cannot be normalized.
        """
        dt = normalize_yyyymmdd_to_datetime(yyyymmdd)
        self._provider = provider_mapping.get(provider, AstralProvider)

        if latitude and longitude:
            latitude, longitude = normalize_coordinates(latitude, longitude)
        self._latitude = latitude
        self._longitude = longitude

        self._attributes = self.provider.calc_sun(
            date=dt,
            latitude=self.latitude,
            longitude=self.longitude,
        )

    def calc_intervals(self, *args, **kwargs):
        return self.provider.calc_intervals(Sun, *args, **kwargs)

    @property
    def latitude(self) -> float:
        return self._latitude

    @property
    def longitude(self) -> float:
        return self._longitude

    @property
    def provider(self) -> LocationProviderType:
        return self._provider

    def time(self, event, get_fallback=lambda: None):
        result = self._attributes.get(event, None)
        if result is None:
            result = get_fallback()
        return result

    @property
    def dawn(self):
        return self.time("dawn")

    @property
    def dawn_lst(self):
        return self.time(
            "dawn_lst", lambda: utc_to_lst(self.time("dawn"), self._latitude, self._longitude)
        )

    @property
    def sunrise(self):
        return self.time("sunrise")

    @property
    def sunrise_lst(self):
        return self.time(
            "sunrise_lst", lambda: utc_to_lst(self.time("sunrise"), self._latitude, self._longitude)
        )

    @property
    def noon(self):
        return self.time("noon")

    @property
    def noon_lst(self):
        return self.time(
            "noon_lst", lambda: utc_to_lst(self.time("noon"), self._latitude, self._longitude)
        )

    @property
    def sunset(self):
        return self.time("sunset")

    @property
    def sunset_lst(self):
        return self.time(
            "sunset_lst", lambda: utc_to_lst(self.time("sunset"), self._latitude, self._longitude)
        )

    @property
    def dusk(self):
        return self.time("dusk")

    @property
    def dusk_lst(self):
        return self.time(
            "dusk_lst", lambda: utc_to_lst(self.time("dusk"), self._latitude, self._longitude)
        )
