from typing import Any
from uuid import UUID

from src.domain.actuators.ports import ActuatorPort
from src.infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRunTimeExceededError,
)


class LoggingActuatorDecorator(ActuatorPort):
    def __init__(self, inner: ActuatorPort, log_repository):
        self.inner = inner
        self.log_repository = log_repository

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        try:
            self.inner.apply(
                device_id=device_id,
                command=command,
                payload=payload,
            )

        except MaxRunTimeExceededError:
            self.log_repository.create(
                device_id=device_id,
                success=False,
                policy_applied=["maxRunTime", "logging"],
                message="Max run time exceeded",
            )
            raise

        except Exception as error:
            self.log_repository.create(
                device_id=device_id,
                success=False,
                policy_applied=["logging"],
                message=str(error),
            )
            raise

        else:
            self.log_repository.create(
                device_id=device_id,
                success=True,
                policy_applied=["logging"],
                message=None,
            )
