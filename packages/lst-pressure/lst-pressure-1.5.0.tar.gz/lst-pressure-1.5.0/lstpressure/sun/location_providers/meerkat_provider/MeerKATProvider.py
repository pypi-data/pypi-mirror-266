from ..LocationProvider import LocationProvider
from datetime import date, datetime, time, timedelta
from .DateTimeUtils import DateTimeUtil
from ....lstindex import LSTInterval
from .SolarSystemUtils import SolarSystem
from .AstroUtils import AstroUtil
import json
import os
from logger import warn
from perf import track_total_runtime, decorate_all
from ..normalize_intervals import normalize_interval
from conf import LocationProviderType as S


@decorate_all(track_total_runtime)
class MeerKATProvider(LocationProvider):
    @staticmethod
    def calc_sun(date: date, latitude, longitude):
        date = datetime.combine(date, time(0))
        with open(os.path.join(os.path.dirname(__file__), "planets.json"), "r") as f:
            planets = json.load(f)

            jd = DateTimeUtil.jd(date)
            sun_pos = SolarSystem.sunpos(planets["Earth"], jd)
            sun_lst = calc_sun_rise_set(
                sun_pos["ra"], sun_pos["dec"], AstroUtil.MKAT_POSITION["latitude"], 0
            )

            set_utc = DateTimeUtil.lst2ut(
                sun_lst["lstSet"], AstroUtil.MKAT_POSITION["longitude"], date
            )
            rise_utc = DateTimeUtil.lst2ut(
                sun_lst["lstRise"], AstroUtil.MKAT_POSITION["longitude"], date
            )

            set_date = date.replace(hour=int(set_utc), minute=int((set_utc - int(set_utc)) * 60))
            rise_date = date.replace(
                hour=int(rise_utc), minute=int((rise_utc - int(rise_utc)) * 60)
            )

            return {
                "dawn": None,
                "dusk": None,
                "noon": None,
                "sunrise": rise_date,
                "sunrise_lst": sun_lst["lstRise"],
                "sunset": set_date,
                "sunset_lst": sun_lst["lstSet"],
            }

    @staticmethod
    def calc_intervals(
        Sun, latitude: str | float, longitude: str | float, today_dt: datetime, obj=None
    ) -> list[LSTInterval]:
        # Interpreter sees this as a module if at the top of the file
        from ....lstindex import LSTIntervalType, LSTInterval

        if latitude or longitude:
            warn(
                "MEERKAT sub provider doesn't allow for overriding latitude and longitude values. Provided values will be ignored."
            )

        today = today_dt
        today_sun = Sun(today, provider=S.MEERKAT)
        today_sunrise_lst = today_sun.sunrise_lst
        today_sunrise_utc = today_sun.sunrise
        today_sunset_lst = today_sun.sunset_lst
        today_sunset_utc = today_sun.sunset

        tomorrow = today + timedelta(days=1)
        tomorrow_sun = Sun(tomorrow, provider=S.MEERKAT)
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
            *normalize_interval(today_sunset_lst, tomorrow_sunrise_lst),
            today_sunset_utc.strftime("%H:%M"),
            tomorrow_sunrise_utc.strftime("%H:%M"),
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
                    tomorrow_sunrise_lst,
                    0,
                    tomorrow_sunrise_utc.strftime("%H:%M"),
                    obj,
                    today,
                    LSTIntervalType.NIGHT,
                    today_sun,
                    tomorrow_sun,
                )
            )

        return result


@track_total_runtime
def calc_sun_rise_set(
    ra: float | str,
    dec: float | str,
    latitude: float | str,
    thresh_hold: float | str,
):
    cos_h = -(AstroUtil.sind(thresh_hold) + AstroUtil.sind(latitude) * AstroUtil.sind(dec)) / (
        AstroUtil.cosd(latitude) * AstroUtil.cosd(dec)
    )
    obj = {
        "never_up": False,
        "circumpolar": False,
        "lstRise": 0,
        "lstSet": 0,
    }
    ha = AstroUtil.acosd(cos_h) / 15.0
    ra_hours = ra / 15.0  # Convert RA to hours
    obj["lstRise"] = AstroUtil.rev24(ra_hours - ha)
    obj["lstSet"] = AstroUtil.rev24(ra_hours + ha)
    return obj
