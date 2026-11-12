from src.domain.actuators.ports import ActuatorPort
from src.domain.commands.base import Command


class StartGrowLightCommand(Command):
    command_type = "start_grow_light"
    target_state = "running"

    def execute(self, port: ActuatorPort) -> None:
        self.apply(port)


class StopGrowLightCommand(Command):
    command_type = "stop_grow_light"
    target_state = "idle"

    def execute(self, port: ActuatorPort) -> None:
        self.apply(port)


class SetLightLevelCommand(Command):
    command_type = "set_light_level"
    target_state = None

    def execute(self, port: ActuatorPort) -> None:
        level = self.payload.get("level", 1)

        if isinstance(level, bool) or not isinstance(level, (int, float)):
            raise ValueError("Light level must be a number.")

        if not 0 <= level <= 100:
            raise ValueError("Light level must be between 0 and 100.")

        self.payload["level"] = level
        self.apply(port)
