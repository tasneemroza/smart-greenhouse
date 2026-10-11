
from src.application.devices.family_service import DeviceFamilyService
from src.domain.devices.entity import Device
from src.domain.devices.family_factory import (
    EdgeHardwareFactory,
    SimulationDeviceFactory,
)


class FakeDeviceRepository:
    def __init__(self):
        self.devices: list[Device] = []
        self.save_calls = 0

    def list_devices(
        self,
        device_family: str | None = None,
        role: str | None = None,
    ) -> list[Device]:
        devices = self.devices

        if device_family is not None:
            devices = [
                device for device in devices
                if device.device_family == device_family
            ]

        if role is not None:
            devices = [
                device for device in devices
                if device.role == role
            ]

        return devices

    def save_devices(self, devices: list[Device]) -> list[Device]:
        self.save_calls += 1
        self.devices.extend(devices)
        return devices


def test_simulation_factory_returns_four_devices():
    devices = SimulationDeviceFactory().create_device_set()

    assert len(devices) == 4
    assert sum(device.role == "sensor" for device in devices) == 2
    assert sum(device.role == "actuator" for device in devices) == 2
    assert all(device.device_family == "simulation" for device in devices)


def test_edge_factory_differs_from_simulation():
    simulation_devices = SimulationDeviceFactory().create_device_set()
    edge_devices = EdgeHardwareFactory().create_device_set()

    assert len(edge_devices) == 4
    assert sum(device.role == "sensor" for device in edge_devices) == 2
    assert sum(device.role == "actuator" for device in edge_devices) == 2
    assert all(device.device_family == "edge" for device in edge_devices)

    simulation_configs = [
        device.default_config for device in simulation_devices
    ]
    edge_configs = [
        device.default_config for device in edge_devices
    ]

    assert simulation_configs != edge_configs


def test_repeated_provisioning_does_not_create_duplicates():
    repository = FakeDeviceRepository()
    service = DeviceFamilyService(repository)

    first_result = service.provision_family("simulation")
    second_result = service.provision_family("simulation")

    assert len(first_result) == 4
    assert len(second_result) == 4
    assert len(repository.devices) == 4
    assert repository.save_calls == 1


def test_provisioning_creates_only_missing_devices():
    repository = FakeDeviceRepository()
    service = DeviceFamilyService(repository)

    initial_devices = SimulationDeviceFactory().create_device_set()
    repository.devices.extend(initial_devices[:3])

    result = service.provision_family("simulation")

    assert len(result) == 4
    assert len(repository.devices) == 4
    assert repository.save_calls == 1
