from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select

from src.application.sensors.reading_dto import ReadingDto
from src.domain.sensors.reading import Reading
from src.infrastructure.adapters.sensors.mqtt import MqttSensorAdapter
from src.infrastructure.adapters.sensors.simulation import SimulationSensorAdapter
from src.infrastructure.adapters.sensors.vendor_stub import VendorSensorAdapter
from src.infrastructure.persistence.models import DeviceRow


class ReadingIngest:
    def __init__(self, db, repository):
        self.db = db
        self.repository = repository

    def take_reading(
        self,
        device_id: UUID,
        now: datetime | None = None,
    ) -> ReadingDto:
        device = self._get_device(device_id)

        timestamp = now or datetime.now(timezone.utc)

        if timestamp.tzinfo is None:
            raise ValueError("now must be timezone-aware")

        reading = self._create_reading(device, timestamp)

        return self.record(device_id, reading)

    def record(
        self,
        device_id: UUID,
        reading: Reading,
    ) -> ReadingDto:
        if reading.device_id != device_id:
            raise ValueError("Reading device_id does not match device_id")

        saved = self.repository.save(reading)

        return ReadingDto.model_validate(saved)

    def list_readings(
        self,
        device_id: UUID,
        limit: int = 20,
    ) -> list[ReadingDto]:
        self._get_device(device_id)

        readings = self.repository.list_for_device(
            device_id=device_id,
            limit=limit,
        )

        return [
            ReadingDto.model_validate(reading)
            for reading in readings
        ]

    def read(
        self,
        device_id: UUID,
        now: datetime | None = None,
    ) -> ReadingDto:
        return self.take_reading(device_id, now=now)

    def _get_device(self, device_id: UUID) -> DeviceRow:
        device = self.db.scalars(
            select(DeviceRow).where(DeviceRow.id == device_id)
        ).first()

        if device is None:
            raise ValueError("Sensor not found")

        if device.role != "sensor":
            raise ValueError("Device is not a sensor")

        return device

    def _create_reading(
        self,
        device: DeviceRow,
        now: datetime,
    ) -> Reading:
        config = device.default_config or {}
        protocol = str(config.get("protocol", "simulation")).lower()
        unit = str(config.get("unit", "unknown"))

        if protocol in {"simulation", "sim"}:
            adapter = SimulationSensorAdapter(
                device_id=device.id,
                device_type=device.device_type,
                unit=unit,
            )
            return adapter.read(now=now)

        if protocol == "mqtt":
            raise ValueError(
                "MQTT sensor requires an inbound payload"
            )

        if protocol == "vendor":
            adapter = VendorSensorAdapter(
                device_id=device.id,
                unit=unit,
            )
            raw_value = config.get("value")

            if raw_value is None:
                raise ValueError(
                    "Vendor sensor requires a configured value"
                )

            return adapter.read(
                raw_value=float(raw_value),
                raw_unit=unit,
                timestamp=now,
            )

        raise ValueError(
            f"Unsupported sensor protocol: {protocol}"
        )