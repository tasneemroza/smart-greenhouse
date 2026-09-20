from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.devices.entity import Device
from src.domain.sensors.entity import Sensor
from src.infrastructure.persistence.models import DeviceRow


class DeviceRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_sensor(self, sensor: Sensor) -> Sensor:
        device = DeviceRow(
            device_type=sensor.device_type,
            role="sensor",
            device_family="simulation",
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

    def save_device(self, device: Device) -> Device:
        row = DeviceRow(
            device_type=device.device_type,
            role=device.role,
            device_family=device.device_family,
            display_name=device.display_name,
            default_config=device.default_config,
        )

        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)

        return self._row_to_device(row)

    def save_devices(self, devices: list[Device]) -> list[Device]:
        rows = [
            DeviceRow(
                device_type=device.device_type,
                role=device.role,
                device_family=device.device_family,
                display_name=device.display_name,
                default_config=device.default_config,
            )
            for device in devices
        ]

        self.db.add_all(rows)
        self.db.commit()

        for row in rows:
            self.db.refresh(row)

        return [self._row_to_device(row) for row in rows]

    def list_devices(
        self,
        *,
        device_family: str | None = None,
        role: str | None = None,
    ) -> list[Device]:
        statement = select(DeviceRow)

        if device_family is not None:
            statement = statement.where(
                DeviceRow.device_family == device_family
            )

        if role is not None:
            statement = statement.where(DeviceRow.role == role)

        statement = statement.order_by(DeviceRow.created_at.desc())

        rows = self.db.scalars(statement).all()

        return [self._row_to_device(row) for row in rows]

    @staticmethod
    def _row_to_device(row: DeviceRow) -> Device:
        return Device(
            id=row.id,
            device_type=row.device_type,
            role=row.role,
            device_family=row.device_family,
            display_name=row.display_name or row.device_type,
            default_config=row.default_config,
        )