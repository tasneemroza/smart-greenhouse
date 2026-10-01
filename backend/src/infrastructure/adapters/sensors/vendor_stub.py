from datetime import datetime, timezone
from uuid import UUID

from src.domain.sensors.ports import SensorPort
from src.domain.sensors.reading import Reading


class VendorSensorAdapter(SensorPort):
    def __init__(
        self,
        device_id: UUID,
        unit: str,
    ):
        self.device_id = device_id
        self.unit = unit

    def read(
        self,
        raw_value: float,
        raw_unit: str,
        timestamp: datetime | None = None,
    ) -> Reading:
        recorded_at = timestamp or datetime.now(timezone.utc)

        return Reading(
            device_id=self.device_id,
            value=float(raw_value),
            unit=raw_unit or self.unit,
            source="vendor",
            recorded_at=recorded_at,
        )