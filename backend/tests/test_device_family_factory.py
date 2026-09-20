from src.domain.devices.family_factory import (
    EdgeHardwareFactory,
    SimulationDeviceFactory,
)


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