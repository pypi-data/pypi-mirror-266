from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Optional
from ...lstindex import LSTInterval


class LocationProvider(ABC):
    @staticmethod
    @abstractmethod
    def calc_sun(date: date, latitude: Optional[float], longitude: Optional[float]) -> dict:
        pass

    @staticmethod
    @abstractmethod
    def calc_intervals(
        latitude: str | float, longitude: str | float, today_dt: datetime, self
    ) -> list[LSTInterval]:
        pass
