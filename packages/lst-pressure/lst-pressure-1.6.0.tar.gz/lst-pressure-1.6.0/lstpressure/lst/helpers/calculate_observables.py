from datetime import datetime
from typing import Optional
from ...observable import Observable
from ...observation import Observation
from ...lstcalendar import LSTCalendar
from perf import track_total_runtime
from conf import LocationProviderType
from typing import Optional


@track_total_runtime
def calculate_observables(
    cal_start: str | datetime,
    cal_end: str | datetime,
    observations: list[Observation],
    latitude: Optional[str | float] = None,
    longitude: Optional[str | float] = None,
    provider: Optional[LocationProviderType] = None,
) -> list[Observable]:
    return sorted(
        LSTCalendar(
            cal_start,
            cal_end,
            observations=observations,
            latitude=latitude,
            longitude=longitude,
            provider=provider,
        ).observables()
    )
