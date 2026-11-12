from datetime import datetime, timedelta, timezone
from typing import Any, Callable
from uuid import UUID

from src.domain.actuators.ports import ActuatorPort


class MaxRunTimeExceededError(Exception):
    def __init__(self):
        super().__init__("Max run time exceeded")


class MaxRunTimeActuatorDecorator(ActuatorPort):
    def __init__(
        self,
        inner: ActuatorPort,
        state_repository,
        clock: Callable[[], datetime] | None = None,
    ):
        self.inner = inner
        self.state_repository = state_repository
        self.clock = clock or (
            lambda: datetime.now(timezone.utc)
        )

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        # Stopping must remain possible even after the runtime limit.
        if command not in {"stop_pump", "stop_grow_light"}:
            state = self.state_repository.get_state(device_id)

            if state is not None and state.state == "running":
                updated_at = state.updated_at

                if updated_at.tzinfo is None:
                    updated_at = updated_at.replace(
                        tzinfo=timezone.utc
                    )

                elapsed = self.clock() - updated_at

                if elapsed >= timedelta(minutes=30):
                    raise MaxRunTimeExceededError()

        self.inner.apply(
            device_id=device_id,
            command=command,
            payload=payload,
        )
