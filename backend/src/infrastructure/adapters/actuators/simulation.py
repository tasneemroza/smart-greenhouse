from typing import Any
from uuid import UUID

from src.domain.actuators.ports import ActuatorPort


class SimulationActuatorAdapter(ActuatorPort):
    def __init__(self):
        self.commands: list[dict[str, Any]] = []

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        self.commands.append(
            {
                "device_id": device_id,
                "command": command,
                "payload": payload or {},
            }
        )

    def get_last_command(self) -> dict[str, Any] | None:
        if not self.commands:
            return None

        return self.commands[-1]