from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.sensors.entity import Sensor
from src.infrastructure.persistence.models import DeviceRow


class DeviceRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_sensor(self, sensor: Sensor) -> Sensor:
        device = DeviceRow(
            device_type=sensor.device_type,
            role="sensor",
            display_name=sensor.display_name,
            default_config=sensor.default_config,
        )

        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)

        return Sensor(
            id=device.id,
            device_type=device.device_type,
            display_name=device.display_name,
            default_config=device.default_config,
        )

    def list_sensors(self) -> list[Sensor]:
        statement = (
            select(DeviceRow)
            .where(DeviceRow.role == "sensor")
            .order_by(DeviceRow.created_at.desc())
        )

        devices = self.db.scalars(statement).all()

        return [
            Sensor(
                id=device.id,
                device_type=device.device_type,
                display_name=device.display_name,
                default_config=device.default_config,
            )
            for device in devices
        ]