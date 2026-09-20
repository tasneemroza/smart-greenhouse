from src.domain.devices.family_factory import get_family_factory
from src.domain.devices.entity import Device
from src.infrastructure.persistence.device_repository import DeviceRepository


class DeviceFamilyService:
    def __init__(self, repository: DeviceRepository):
        self.repository = repository

    def provision_family(self, family: str) -> list[Device]:
        factory = get_family_factory(family)
        devices = factory.create_device_set()
        return self.repository.save_devices(devices)

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