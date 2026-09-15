from uuid import UUID

from src.domain.sensors.entity import Sensor
from src.domain.sensors.creators import CREATOR_REGISTRY
from src.infrastructure.persistence.device_repository import DeviceRepository


class SensorService:
    def __init__(self, repository: DeviceRepository):
        self.repository = repository

    def create_sensor(
        self,
        sensor_type: str,
        display_name: str | None = None,
    ) -> Sensor:
        creator = CREATOR_REGISTRY.get(sensor_type)

        if creator is None:
            raise ValueError(f"Unknown sensor type: {sensor_type}")

        sensor = creator.create_sensor(display_name)

        return self.repository.save(sensor)

    def list_sensors(self) -> list[Sensor]:
        return self.repository.list_sensors()