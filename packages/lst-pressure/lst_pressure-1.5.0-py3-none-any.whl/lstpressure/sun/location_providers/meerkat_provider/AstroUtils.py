import math


class AstroUtil:
    RTD = 180.0 / math.pi
    DTR = math.pi / 180

    MKAT_POSITION = {
        "longitude": 21.443888888888889,
        "latitude": -30.7110555555556,
        "limit": 15,
        "tz": +2,
    }

    @staticmethod
    def sind(angle):
        return math.sin(math.radians(angle))

    @staticmethod
    def asind(angle):
        return AstroUtil.RTD * math.asin(angle)

    @staticmethod
    def cosd(angle):
        return math.cos(math.radians(angle))

    @staticmethod
    def acosd(angle):
        return math.degrees(math.acos(angle))

    @staticmethod
    def atan2d(y, x):
        return math.degrees(math.atan2(y, x))

    @staticmethod
    def tand(angle):
        return math.tan(math.radians(angle))

    @staticmethod
    def rev360(angle):
        return angle % 360

    @staticmethod
    def rev24(hour):
        return hour - (hour // 24.0) * 24.0

    @staticmethod
    def hms(x):
        hms_list = x.split(":")
        hr = int(hms_list[0])
        min = int(hms_list[1])
        sec = float(hms_list[2])
        decimal = hr + min / 60.0 + sec / 3600.0
        return decimal
