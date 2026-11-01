from datetime import datetime, timezone
from uuid import UUID

from src.application.devices.actuator_state_dto import ActuatorStateDto
from src.domain.actuators.state import ActuatorContext
from src.infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)


class ActuatorNotFoundError(LookupError):
    pass


class ActuatorStateNotFoundError(LookupError):
    pass


class ActuatorStateService:
    def __init__(self, repository: ActuatorStateRepository):
        self.repository = repository

    def get_state(self, device_id: UUID) -> ActuatorStateDto:
        device = self.repository.get_actuator(device_id)

        if device is None:
            raise ActuatorNotFoundError("Actuator not found.")

        state_row = self.repository.get_state(device_id)

        if state_row is None:
            raise ActuatorStateNotFoundError(
                "Actuator state has not been initialized."
            )

        context = ActuatorContext(
            state=state_row.state,
            device_type=device.device_type,
        )

        return ActuatorStateDto(
            device_id=device.id,
            state=context.state,
            updated_at=state_row.updated_at,
            allowed_commands=context.allowed_commands(),
        )

    def transition(
        self,
        device_id: UUID,
        target: str,
    ) -> ActuatorStateDto:
        try:
            device = self.repository.get_actuator(device_id)

            if device is None:
                raise ActuatorNotFoundError("Actuator not found.")

            state_row = self.repository.get_state_for_update(device_id)

            if state_row is None:
                raise ActuatorStateNotFoundError(
                    "Actuator state has not been initialized."
                )

            context = ActuatorContext(
                state=state_row.state,
                device_type=device.device_type,
            )

            context.transition(target)

            state_row.state = context.state
            state_row.updated_at = datetime.now(timezone.utc)

            self.repository.save(state_row)

            return ActuatorStateDto(
                device_id=device.id,
                state=context.state,
                updated_at=state_row.updated_at,
                allowed_commands=context.allowed_commands(),
            )

        except Exception:
            self.repository.rollback()
            raise
