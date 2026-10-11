
from src.domain.devices.family_factory import get_family_factory
from src.domain.devices.entity import Device
from src.infrastructure.persistence.device_repository import DeviceRepository


class DeviceFamilyService:
    def __init__(self, repository: DeviceRepository):
        self.repository = repository

    def provision_family(self, family: str) -> list[Device]:
        factory = get_family_factory(family)
        requested_devices = factory.create_device_set()

        existing_devices = self.repository.list_devices(
            device_family=family,
        )

        def device_key(device: Device) -> tuple[str, str, str]:
            return (
                device.role,
                device.device_type,
                device.display_name,
            )

        existing_by_key: dict[tuple[str, str, str], Device] = {}

        for device in reversed(existing_devices):
            existing_by_key.setdefault(device_key(device), device)

        missing_devices = [
            device
            for device in requested_devices
            if device_key(device) not in existing_by_key
        ]

        created_devices = (
            self.repository.save_devices(missing_devices)
            if missing_devices
            else []
        )

        created_by_key = {
            device_key(device): device
            for device in created_devices
        }

        return [
            existing_by_key.get(device_key(device))
            or created_by_key[device_key(device)]
            for device in requested_devices
        ]

    def list_devices(
        self,
        *,
        device_family: str | None = None,
        role: str | None = None,
    ) -> list[Device]:
        return self.repository.list_devices(
            device_family=device_family,
            role=role,
        )
