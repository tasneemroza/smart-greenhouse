from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.persistence.models import (
    ActuatorStateRow,
    DeviceRow,
)


class ActuatorStateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_actuator(self, device_id: UUID) -> DeviceRow | None:
        device = self.db.get(DeviceRow, device_id)

        if device is None or device.role != "actuator":
            return None

        return device

    def get_state(self, device_id: UUID) -> ActuatorStateRow | None:
        return self.db.get(ActuatorStateRow, device_id)

    def get_state_for_update(
        self,
        device_id: UUID,
    ) -> ActuatorStateRow | None:
        statement = (
            select(ActuatorStateRow)
            .where(ActuatorStateRow.device_id == device_id)
            .with_for_update()
        )

        return self.db.scalar(statement)

    def save(self, state: ActuatorStateRow) -> ActuatorStateRow:
        self.db.commit()
        self.db.refresh(state)
        return state

    def rollback(self) -> None:
        self.db.rollback()
