from datetime import datetime, timezone
from uuid import UUID

from src.domain.sensors.ports import SensorPort
from src.domain.sensors.reading import Reading


class MqttSensorAdapter(SensorPort):
    def __init__(
        self,
        device_id: UUID,
        unit: str,
    ):
        self.device_id = device_id
        self.unit = unit

    def read(self, now: datetime | None = None) -> Reading:
        raise RuntimeError("MQTT adapter requires an inbound payload")

    def translate(self, payload: dict) -> Reading:
        value = payload.get("value")

        if value is None:
            raise ValueError("MQTT payload is missing value")

        unit = payload.get("unit") or self.unit

        recorded_at = payload.get("recorded_at")

        if recorded_at is None:
            recorded_at = datetime.now(timezone.utc)
        elif isinstance(recorded_at, str):
            recorded_at = datetime.fromisoformat(
                recorded_at.replace("Z", "+00:00")
            )

        if recorded_at.tzinfo is None:
            recorded_at = recorded_at.replace(tzinfo=timezone.utc)

        return Reading(
            device_id=self.device_id,
            value=float(value),
            unit=unit,
            source="mqtt",
            recorded_at=recorded_at,
        )