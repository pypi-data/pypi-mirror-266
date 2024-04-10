from .AstroUtils import AstroUtil
from .SolarSystemUtils import SolarSystem


class DateTimeUtil:
    # You can implement the local_sidereal function based on your specific need

    @staticmethod
    def local_sidereal(jd):
        # Assuming g_sidereal is implemented elsewhere
        res = SolarSystem.g_sidereal(jd)  # You need to implement g_sidereal

        # Adding longitude and wrapping to 360 degrees
        res += AstroUtil.MKAT_POSITION["longitude"]
        return AstroUtil.rev360(res)

    @staticmethod
    def jd(date):
        yr = date.year
        mon = date.month
        day = date.day
        hr = date.hour
        min = date.minute
        sec = date.second
        fday = day + ((3600.0 * hr + 60.0 * min + sec) / 86400.0)

        if mon <= 2:
            yr -= 1
            mon += 12

        if yr > 1582:  # 1582 October 15
            A = yr // 100
            B = 2 - A + A // 4
        else:
            A = 0
            B = 0

        if yr < 0:
            C = int((365.25 * yr) - 0.75)
        else:
            C = int(365.25 * yr)

        D = int(30.6001 * (mon + 1))

        jd = B + C + D + fday + 1720994.5

        return jd

    @staticmethod
    def lst2gst(lst, longitude):
        return AstroUtil.rev24(lst - (longitude / 15))

    @staticmethod
    def gst2ut(jd, gst):
        S = jd - 2451545.0
        T = S / 36525.0
        T0 = AstroUtil.rev24(6.697374558 + (2400.051336 * T))
        ut = AstroUtil.rev24(gst - T0) * 0.9972695663
        return ut

    @staticmethod
    def lst2ut(lst, longitude, date):
        gst = DateTimeUtil.lst2gst(lst, longitude)
        jd = DateTimeUtil.jd(date)
        return DateTimeUtil.gst2ut(jd, gst)
