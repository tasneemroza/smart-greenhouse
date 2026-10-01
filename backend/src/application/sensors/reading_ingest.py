from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.application.sensors.reading_dto import ReadingDto
from src.domain.sensors.reading import Reading
from src.infrastructure.adapters.sensors.mqtt import MqttSensorAdapter
from src.infrastructure.adapters.sensors.simulation import SimulationSensorAdapter
from src.infrastructure.adapters.sensors.vendor_stub import VendorSensorAdapter
from src.infrastructure.persistence.models import DeviceRow
from src.infrastructure.persistence.reading_repository import ReadingRepository


class ReadingIngest:
    def __init__(
        self,
        db: Session,
        repository: ReadingRepository,
    ):
        self.db = db
        self.repository = repository

    def read(
        self,
        device_id: UUID,
        now: datetime | None = None,
    ) -> ReadingDto:
        device = self._get_device(device_id)

        if device.role != "sensor":
            raise ValueError("Device is not a sensor")

        adapter = self._create_adapter(device)

        if isinstance(adapter, MqttSensorAdapter):
            raise ValueError("MQTT sensor requires an inbound payload")

        if isinstance(adapter, VendorSensorAdapter):
            raise ValueError("Vendor sensor requires raw vendor data")

        reading = adapter.read(now)

        return self.record(reading)

    def record(self, reading: Reading) -> ReadingDto:
        saved = self.repository.save(reading)

        return ReadingDto(
            device_id=saved.device_id,
            value=saved.value,
            unit=saved.unit,
            source=saved.source,
            recorded_at=saved.recorded_at,
        )

    def record_mqtt(
        self,
        device_id: UUID,
        payload: dict,
    ) -> ReadingDto:
        device = self._get_device(device_id)

        if device.role != "sensor":
            raise ValueError("Device is not a sensor")

        unit = self._get_unit(device)
        adapter = MqttSensorAdapter(device.id, unit)
        reading = adapter.translate(payload)

        return self.record(reading)

    def _get_device(self, device_id: UUID) -> DeviceRow:
        device = self.db.scalar(
            select(DeviceRow).where(DeviceRow.id == device_id)
        )

        if device is None:
            raise ValueError("Device not found")

        return device

    def _create_adapter(self, device: DeviceRow):
        config = device.default_config or {}
        protocol = config.get("protocol", "simulation")
        unit = self._get_unit(device)

        if protocol in {"simulation", "sim"}:
            return SimulationSensorAdapter(
                device.id,
                device.device_type,
                unit,
            )

        if protocol == "mqtt":
            return MqttSensorAdapter(
                device.id,
                unit,
            )

        if protocol == "vendor":
            return VendorSensorAdapter(
                device.id,
                unit,
            )

        raise ValueError(f"Unsupported sensor protocol: {protocol}")

    @staticmethod
    def _get_unit(device: DeviceRow) -> str:
        config = device.default_config or {}
        unit = config.get("unit")

        if unit:
            return str(unit)

        if device.device_type == "moisture_sensor":
            return "vwc"

        if device.device_type == "light_sensor":
            return "lux"

        raise ValueError("Sensor unit is missing")