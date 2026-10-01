from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.application.sensors.sampling_config_dto import SamplingConfigDto
from src.infrastructure.persistence.models import DeviceRow


class SamplingService:
    def __init__(self, db: Session):
        self.db = db

    def update(
        self,
        device_id: UUID,
        config: SamplingConfigDto,
    ) -> DeviceRow:
        device = self.db.scalar(
            select(DeviceRow).where(DeviceRow.id == device_id)
        )

        if device is None:
            raise ValueError("Device not found")

        if device.role != "sensor":
            raise ValueError("Device is not a sensor")

        device.sampling_interval_seconds = (
            config.sampling_interval_seconds
        )
        device.tracking_enabled = config.tracking_enabled

        self.db.commit()
        self.db.refresh(device)

        return device