from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.sensors.reading import Reading


class SensorPort(ABC):
    @abstractmethod
    def read(self, now: datetime | None = None) -> Reading:
        raise NotImplementedError