from .AstroUtils import AstroUtil
import numpy as np
import math


class SolarSystem:
    @staticmethod
    def helios(p, jd):
        T = (jd - 2451545.0) / 36525
        T2 = T * T
        T3 = T2 * T
        N = AstroUtil.rev360(p["N"][0] + p["N"][1] * T + p["N"][2] * T2 + p["N"][3] * T3)
        i = p["i"][0] + p["i"][1] * T + p["i"][2] * T2 + p["i"][3] * T3
        L = AstroUtil.rev360(p["L"][0] + p["L"][1] * T + p["L"][2] * T2 + p["L"][3] * T3)
        a = p["a"][0] + p["a"][1] * T + p["a"][2] * T2 + p["a"][3] * T3
        e = p["e"][0] + p["e"][1] * T + p["e"][2] * T2 + p["e"][3] * T3
        P = AstroUtil.rev360(p["P"][0] + p["P"][1] * T + p["P"][2] * T2 + p["P"][3] * T3)
        M = AstroUtil.rev360(L - P)
        w = AstroUtil.rev360(L - N - M)

        E0 = M + (AstroUtil.RTD * e * AstroUtil.sind(M) * (1 + e * AstroUtil.cosd(M)))
        E = E0 - (E0 - AstroUtil.RTD * e * AstroUtil.sind(E0) - M) / (1 - e * AstroUtil.cosd(E0))

        while abs(E0 - E) > 0.0005:
            E0 = E
            E = E0 - (E0 - AstroUtil.RTD * e * AstroUtil.sind(E0) - M) / (
                1 - e * AstroUtil.cosd(E0)
            )

        x = a * (AstroUtil.cosd(E) - e)
        y = a * math.sqrt(1 - e * e) * AstroUtil.sind(E)
        r = math.sqrt(x * x + y * y)
        v = AstroUtil.rev360(AstroUtil.atan2d(y, x))

        xeclip = r * (
            AstroUtil.cosd(N) * AstroUtil.cosd(v + w)
            - AstroUtil.sind(N) * AstroUtil.sind(v + w) * AstroUtil.cosd(i)
        )
        yeclip = r * (
            AstroUtil.sind(N) * AstroUtil.cosd(v + w)
            + AstroUtil.cosd(N) * AstroUtil.sind(v + w) * AstroUtil.cosd(i)
        )
        zeclip = r * AstroUtil.sind(v + w) * AstroUtil.sind(i)

        return [xeclip, yeclip, zeclip]

    @staticmethod
    def radecr(obj, base, jd):
        # Equatorial co-ordinates
        x = obj[0]
        y = obj[1]
        z = obj[2]

        # Obliquity of Ecliptic
        obl = 23.4393 - 3.563e-7 * (jd - 2451543.5)

        # Convert to Geocentric co-ordinates
        x1 = x - base[0]
        y1 = (y - base[1]) * AstroUtil.cosd(obl) - (z - base[2]) * AstroUtil.sind(obl)
        z1 = (y - base[1]) * AstroUtil.sind(obl) + (z - base[2]) * AstroUtil.cosd(obl)

        # RA and dec
        ra = AstroUtil.rev360(AstroUtil.atan2d(y1, x1)) / 15.0
        dec = AstroUtil.atan2d(z1, math.sqrt(x1 * x1 + y1 * y1))

        # Earth distance
        r = math.sqrt(x1 * x1 + y1 * y1 + z1 * z1)

        return [ra, dec, r]

    @staticmethod
    def equ_to_horizon(obj, jd):
        from .DateTimeUtils import DateTimeUtil

        ra = obj["ra"]
        dec = obj["dec"]

        # Calculate Hour Angle
        H = DateTimeUtil.local_sidereal(jd) - ra
        sinH = AstroUtil.sind(H)
        cosH = AstroUtil.cosd(H)

        sinl = AstroUtil.sind(AstroUtil.MKAT_POSITION["longitude"])
        cosl = AstroUtil.cosd(AstroUtil.MKAT_POSITION["latitude"])
        sind = AstroUtil.sind(dec)
        cosd = AstroUtil.cosd(dec)
        tand = AstroUtil.tand(dec)

        # Calculate Azimuth and Elevation
        az = AstroUtil.rev360(AstroUtil.atan2d(sinH, cosH * sinl - tand * cosl) + 180)
        el = AstroUtil.asind(sinl * sind + cosl * cosd * cosH)

        obj["azimuth"] = az
        obj["elevation"] = el

        return [az, el]

    @staticmethod
    def g_sidereal(jd):
        T = (jd - 2451545.0) / 36525
        res = (
            280.46061837
            + 360.98564736629 * (jd - 2451545.0)
            + 0.000387933 * T**2
            - T**3 / 38710000
        )
        return AstroUtil.rev360(res)

    @staticmethod
    def sunpos(planet, jd):
        sun_xyz = np.array([0.0, 0.0, 0.0])
        planet_xyz = SolarSystem.helios(planet, jd)
        radec = SolarSystem.radecr(sun_xyz, planet_xyz, jd)
        ra = 15 * radec[0]
        dec = radec[1]
        altaz = SolarSystem.equ_to_horizon({"ra": ra, "dec": dec}, jd)

        return {
            "ra": ra,
            "dec": dec,
            "azimuth": altaz[0],
            "elevation": altaz[1],
            "isVisible": altaz[1] > 0,
        }
