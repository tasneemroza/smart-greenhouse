from src.application.devices.dto import DeviceDto
from src.domain.devices.entity import Device


def device_to_dto(device: Device) -> DeviceDto:
    return DeviceDto(
        id=device.id,
        device_type=device.device_type,
        role=device.role,
        device_family=device.device_family,
        display_name=device.display_name,
        default_config=device.default_config,
        location_id=device.location_id,
        zone_id=device.zone_id,
    )


def devices_to_dtos(devices: list[Device]) -> list[DeviceDto]:
    return [device_to_dto(device) for device in devices]