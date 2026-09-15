from abc import ABC, abstractmethod

from src.domain.sensors.entity import Sensor


class SensorCreator(ABC):
    @abstractmethod
    def create_sensor(self, display_name: str | None = None) -> Sensor:
        pass


class MoistureSensorCreator(SensorCreator):
    def create_sensor(self, display_name: str | None = None) -> Sensor:
        return Sensor(
            id=None,
            device_type="moisture",
            display_name=display_name or "Moisture Sensor",
            default_config={
                "threshold": 40,
                "unit": "percent",
            },
        )


class LightSensorCreator(SensorCreator):
    def create_sensor(self, display_name: str | None = None) -> Sensor:
        return Sensor(
            id=None,
            device_type="light",
            display_name=display_name or "Light Sensor",
            default_config={
                "threshold": 500,
                "unit": "lux",
            },
        )


CREATOR_REGISTRY: dict[str, SensorCreator] = {
    "moisture": MoistureSensorCreator(),
    "light": LightSensorCreator(),
}