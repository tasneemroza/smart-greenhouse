from typing import Any
from uuid import UUID

from src.domain.actuators.ports import ActuatorPort
from src.domain.commands.base import Command
from src.domain.commands.light import (
    StartGrowLightCommand,
    StopGrowLightCommand,
    SetLightLevelCommand,
)
from src.domain.commands.pump import StartPumpCommand, StopPumpCommand


COMMAND_REGISTRY: dict[str, type[Command]] = {
    StartPumpCommand.command_type: StartPumpCommand,
    StopPumpCommand.command_type: StopPumpCommand,
    StartGrowLightCommand.command_type: StartGrowLightCommand,
    StopGrowLightCommand.command_type: StopGrowLightCommand,
    SetLightLevelCommand.command_type: SetLightLevelCommand,
}


def command_for(
    command_type: str,
    device_id: UUID,
    payload: dict[str, Any] | None = None,
) -> Command:
    command_class = COMMAND_REGISTRY.get(command_type)

    if command_class is None:
        raise ValueError(f"Unknown command type: {command_type}")

    return command_class(device_id=device_id, payload=payload)


class CommandInvoker:
    def run(self, command: Command, port: ActuatorPort) -> None:
        command.execute(port)
