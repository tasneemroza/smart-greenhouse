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
            device_type="moisture_sensor",
            display_name=display_name or "Moisture Sensor",
            default_config={
                "sampling_interval_seconds": 300,
                "unit": "vwc",
                "threshold": 40,
            },
        )


class LightSensorCreator(SensorCreator):
    def create_sensor(self, display_name: str | None = None) -> Sensor:
        return Sensor(
            id=None,
            device_type="light_sensor",
            display_name=display_name or "Light Sensor",
            default_config={
                "sampling_interval_seconds": 300,
                "unit": "lux",
                "threshold": 500,
            },
        )


CREATOR_REGISTRY: dict[str, SensorCreator] = {
    "moisture": MoistureSensorCreator(),
    "light": LightSensorCreator(),
}


def get_creator(sensor_type: str) -> SensorCreator:
    creator = CREATOR_REGISTRY.get(sensor_type)

    if creator is None:
        raise ValueError(f"Unknown sensor type: {sensor_type}")

    return creator