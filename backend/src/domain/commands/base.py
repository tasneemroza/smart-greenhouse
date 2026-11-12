from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from src.domain.actuators.ports import ActuatorPort


class Command(ABC):
    command_type: str
    target_state: str | None = None

    def __init__(
        self,
        device_id: UUID,
        payload: dict[str, Any] | None = None,
    ):
        self.device_id = device_id
        self.payload = payload or {}

    @abstractmethod
    def execute(self, port: ActuatorPort) -> None:
        raise NotImplementedError

    def apply(self, port: ActuatorPort) -> None:
        port.apply(
            device_id=self.device_id,
            command=self.command_type,
            payload=self.payload,
        )
