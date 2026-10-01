from uuid import UUID

from .dto import ZoneDeviceDto


class DeviceZoneAssignmentService:
    def __init__(self, repository) -> None:
        self._repository = repository

    def assign(
        self,
        device_id: UUID,
        zone_id: UUID | None,
    ):
        return self._repository.assign_device_to_zone(
            device_id=device_id,
            zone_id=zone_id,
        )

    def list_zone_devices(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> list[ZoneDeviceDto] | None:
        devices = self._repository.list_zone_devices(
            location_id=location_id,
            zone_id=zone_id,
        )

        if devices is None:
            return None

        return [
            ZoneDeviceDto(
                id=device.id,
                device_type=device.device_type,
                role=device.role,
                display_name=device.display_name,
            )
            for device in devices
        ]