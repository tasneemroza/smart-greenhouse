from abc import ABC, abstractmethod

from src.domain.devices.entity import Device
from src.domain.sensors.creators import (
    LightSensorCreator,
    MoistureSensorCreator,
)


class DeviceFamilyFactory(ABC):
    @property
    @abstractmethod
    def family_key(self) -> str:
        pass

    @abstractmethod
    def create_device_set(self) -> list[Device]:
        pass


class SimulationDeviceFactory(DeviceFamilyFactory):
    @property
    def family_key(self) -> str:
        return "simulation"

    def create_device_set(self) -> list[Device]:
        moisture_sensor = MoistureSensorCreator().create_sensor(
            "Sim moisture sensor"
        )
        light_sensor = LightSensorCreator().create_sensor(
            "Sim light sensor"
        )

        return [
            Device(
                id=moisture_sensor.id,
                device_type=moisture_sensor.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=moisture_sensor.display_name,
                default_config={
                    **moisture_sensor.default_config,
                    "protocol": "sim",
                },
            ),
            Device(
                id=light_sensor.id,
                device_type=light_sensor.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=light_sensor.display_name,
                default_config={
                    **light_sensor.default_config,
                    "protocol": "sim",
                },
            ),
            Device(
                id=None,
                device_type="water_pump",
                role="actuator",
                device_family=self.family_key,
                display_name="Sim irrigation pump",
                default_config={
                    "protocol": "sim",
                    "power": "low",
                },
            ),
            Device(
                id=None,
                device_type="grow_light",
                role="actuator",
                device_family=self.family_key,
                display_name="Sim grow light",
                default_config={
                    "protocol": "sim",
                    "power": "medium",
                },
            ),
        ]


class EdgeHardwareFactory(DeviceFamilyFactory):
    @property
    def family_key(self) -> str:
        return "edge"

    def create_device_set(self) -> list[Device]:
        moisture_sensor = MoistureSensorCreator().create_sensor(
            "Edge moisture sensor"
        )
        light_sensor = LightSensorCreator().create_sensor(
            "Edge light sensor"
        )

        return [
            Device(
                id=moisture_sensor.id,
                device_type=moisture_sensor.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=moisture_sensor.display_name,
                default_config={
                    **moisture_sensor.default_config,
                    "protocol": "gpio-stub",
                },
            ),
            Device(
                id=light_sensor.id,
                device_type=light_sensor.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=light_sensor.display_name,
                default_config={
                    **light_sensor.default_config,
                    "protocol": "gpio-stub",
                },
            ),
            Device(
                id=None,
                device_type="water_pump",
                role="actuator",
                device_family=self.family_key,
                display_name="Edge irrigation pump",
                default_config={
                    "protocol": "gpio-stub",
                    "pin": 17,
                },
            ),
            Device(
                id=None,
                device_type="grow_light",
                role="actuator",
                device_family=self.family_key,
                display_name="Edge grow light",
                default_config={
                    "protocol": "gpio-stub",
                    "pin": 18,
                },
            ),
        ]


def get_family_factory(family: str) -> DeviceFamilyFactory:
    factories: dict[str, DeviceFamilyFactory] = {
        "simulation": SimulationDeviceFactory(),
        "edge": EdgeHardwareFactory(),
    }

    factory = factories.get(family)

    if factory is None:
        raise ValueError(f"Unknown device family: {family}")

    return factory