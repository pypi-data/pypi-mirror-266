from lstpressure import lstcalendar, lst, lstindex, observable, observation, utils, sun
from lstpressure.lstcalendar import LSTCalendar
from lstpressure.lst import LST
from lstpressure.lstindex import LSTIntervalType
from lstpressure.observable.Observable import Observable
from lstpressure.observation import is_observable, Observation
from lstpressure.sun import Sun
from conf import LocationProviderType, Conf as LSTConf

try:
    import katversion as _katversion
except ImportError:
    import time as _time

    __version__ = "0.0+unknown.{}".format(_time.strftime("%Y%m%d%H%M"))
else:
    __version__ = _katversion.get_version()

__all__ = [
    "__version__",
    "is_observable",
    "lstcalendar",
    "LSTCalendar",
    "LST",
    "lst",
    "lstindex",
    "LSTIntervalType",
    "observable",
    "Observable",
    "observables",
    "observation",
    "Observation",
    "sun",
    "Sun",
    "utils",
    "LSTConf",
    "LocationProviderType",
]

# Automatically added by katversion
__version__ = '1.5.0'
