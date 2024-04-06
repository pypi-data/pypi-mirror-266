from ....lstindex import LSTInterval
from datetime import datetime, timedelta
from ..LocationProvider import LocationProvider
from astral.sun import sun as calc_sun
from astral import LocationInfo
from perf import track_total_runtime, decorate_all
from ....utils import normalize_coordinates
from ..normalize_intervals import normalize_interval


@decorate_all(track_total_runtime)
class AstralProvider(LocationProvider):
    @staticmethod
    def calc_sun(latitude, longitude, date):
        location = LocationInfo(latitude=latitude, longitude=longitude)
        location.timezone = "UTC"
        return calc_sun(location.observer, date=date)

    @staticmethod
    def calc_intervals(
        Sun, latitude: str | float, longitude: str | float, today_dt: datetime, obj
    ) -> list[LSTInterval]:
        # Interpreter sees this as a module if at the top of the file
        from ....lstindex import LSTIntervalType, LSTInterval

        latitude, longitude = normalize_coordinates(latitude, longitude)
        today = today_dt
        today_sun = Sun(today, latitude, longitude, provider=AstralProvider)
        today_sunrise_lst = today_sun.sunrise_lst
        today_sunrise_utc = today_sun.sunrise
        today_sunset_lst = today_sun.sunset_lst
        today_sunset_utc = today_sun.sunset
        today_dusk_lst = today_sun.dusk_lst
        today_dusk_utc = today_sun.dusk

        tomorrow = today + timedelta(days=1)
        tomorrow_sun = Sun(tomorrow, latitude, longitude, provider=AstralProvider)
        tomorrow_dawn_lst = tomorrow_sun.dawn_lst
        tomorrow_dawn_utc = tomorrow_sun.dawn
        tomorrow_sunrise_lst = tomorrow_sun.sunrise_lst
        tomorrow_sunrise_utc = tomorrow_sun.sunrise
        tomorrow_sunset_lst = tomorrow_sun.sunset_lst
        tomorrow_sunset_utc = tomorrow_sun.sunset

        result = []

        # ALL DAY
        result.append(
            LSTInterval(
                0, 24, None, None, obj, today, LSTIntervalType.ALL_DAY, today_sun, tomorrow_sun
            )
        )

        # SUNRISE_SUNSET
        SUNRISE_SUNSET = LSTInterval(
            *normalize_interval(today_sunrise_lst, today_sunset_lst),
            today_sunrise_utc.strftime("%H:%M"),
            today_sunset_utc.strftime("%H:%M"),
            obj,
            today,
            LSTIntervalType.SUNRISE_SUNSET,
            today_sun,
            tomorrow_sun,
        )
        result.append(SUNRISE_SUNSET)
        if SUNRISE_SUNSET.end > 24:
            result.append(
                LSTInterval(
                    0,
                    tomorrow_sunset_lst,
                    today_sunrise_utc.strftime("%H:%M"),
                    tomorrow_sunset_utc.strftime("%H:%M"),
                    obj,
                    today,
                    LSTIntervalType.SUNRISE_SUNSET,
                    today_sun,
                    tomorrow_sun,
                )
            )

        # SUNSET_SUNRISE
        SUNSET_SUNRISE = LSTInterval(
            *normalize_interval(today_sunset_lst, tomorrow_sunrise_lst),
            today_sunset_utc.strftime("%H:%M"),
            tomorrow_sunrise_utc.strftime("%H:%M"),
            obj,
            today,
            LSTIntervalType.SUNSET_SUNRISE,
            today_sun,
            tomorrow_sun,
        )
        result.append(SUNSET_SUNRISE)

        if SUNSET_SUNRISE.end > 24:
            result.append(
                LSTInterval(
                    0,
                    tomorrow_sunrise_lst,
                    0,
                    tomorrow_sunrise_utc.strftime("%H:%M"),
                    obj,
                    today,
                    LSTIntervalType.SUNSET_SUNRISE,
                    today_sun,
                    tomorrow_sun,
                )
            )

        # NIGHT
        NIGHT = LSTInterval(
            *normalize_interval(today_dusk_lst, tomorrow_dawn_lst),
            today_dusk_utc.strftime("%H:%M"),
            tomorrow_dawn_utc.strftime("%H:%M"),
            obj,
            today,
            LSTIntervalType.NIGHT,
            today_sun,
            tomorrow_sun,
        )
        result.append(NIGHT)

        if NIGHT.end > 24:
            result.append(
                LSTInterval(
                    0,
                    tomorrow_dawn_lst,
                    0,
                    tomorrow_dawn_utc.strftime("%H:%M"),
                    obj,
                    today,
                    LSTIntervalType.NIGHT,
                    today_sun,
                    tomorrow_sun,
                )
            )

        return result
