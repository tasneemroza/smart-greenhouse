import random
from datetime import datetime, timezone
from uuid import UUID

from src.domain.sensors.ports import SensorPort
from src.domain.sensors.reading import Reading


class SimulationSensorAdapter(SensorPort):
    def __init__(
        self,
        device_id: UUID,
        device_type: str,
        unit: str,
    ):
        self.device_id = device_id
        self.device_type = device_type
        self.unit = unit

    def read(self, now: datetime | None = None) -> Reading:
        recorded_at = now or datetime.now(timezone.utc)

        if self.device_type == "moisture_sensor":
            value = random.uniform(30.0, 70.0)
        elif self.device_type == "light_sensor":
            value = random.uniform(100.0, 1000.0)
        else:
            value = random.uniform(0.0, 100.0)

        return Reading(
            device_id=self.device_id,
            value=value,
            unit=self.unit,
            source="simulation",
            recorded_at=recorded_at,
        )