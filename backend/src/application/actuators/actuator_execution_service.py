from uuid import UUID

from sqlalchemy.orm import Session

from src.application.devices.actuator_state_service import (
    ActuatorNotFoundError,
    ActuatorStateNotFoundError,
)
from src.infrastructure.adapters.actuators.logging_decorator import (
    LoggingActuatorDecorator,
)
from src.infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRunTimeActuatorDecorator,
)
from src.infrastructure.adapters.actuators.simulation import (
    SimulationActuatorAdapter,
)
from src.infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)
from src.infrastructure.persistence.execution_log_repository import (
    ExecutionLogRepository,
)


class ActuatorExecutionService:
    def __init__(self, db: Session):
        self.log_repository = ExecutionLogRepository(db)
        self.state_repository = ActuatorStateRepository(db)

        simulation = SimulationActuatorAdapter()

        runtime_policy = MaxRunTimeActuatorDecorator(
            inner=simulation,
            state_repository=self.state_repository,
        )

        self.actuator = LoggingActuatorDecorator(
            inner=runtime_policy,
            log_repository=self.log_repository,
        )

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict | None = None,
    ) -> None:
        device = self.state_repository.get_actuator(device_id)

        if device is None:
            raise ActuatorNotFoundError("Actuator not found.")

        state = self.state_repository.get_state(device_id)

        if state is None:
            raise ActuatorStateNotFoundError(
                "Actuator state has not been initialized."
            )

        self.actuator.apply(
            device_id=device_id,
            command=command,
            payload=payload,
        )

    def list_recent(self, limit: int = 20):
        return self.log_repository.list_recent(limit)
