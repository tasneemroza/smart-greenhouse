from enum import Enum


class ActuatorState(str, Enum):
    OFF = "off"
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    MAINTENANCE = "maintenance"


ALLOWED_TRANSITIONS = {
    ActuatorState.OFF: {
        ActuatorState.IDLE,
        ActuatorState.ERROR,
    },
    ActuatorState.IDLE: {
        ActuatorState.RUNNING,
        ActuatorState.OFF,
        ActuatorState.MAINTENANCE,
        ActuatorState.ERROR,
    },
    ActuatorState.RUNNING: {
        ActuatorState.IDLE,
        ActuatorState.MAINTENANCE,
        ActuatorState.ERROR,
    },
    ActuatorState.MAINTENANCE: {
        ActuatorState.IDLE,
        ActuatorState.OFF,
        ActuatorState.ERROR,
    },
    ActuatorState.ERROR: {
        ActuatorState.IDLE,
    },
}


class InvalidActuatorTransition(ValueError):
    pass


class ActuatorContext:
    def __init__(self, state: str, device_type: str):
        self._state = ActuatorState(state)
        self._device_type = device_type

    @property
    def state(self) -> str:
        return self._state.value

    def allowed_commands(self) -> list[str]:
        command_names = {
            "water_pump": "pump",
            "test_pump": "pump",
            "grow_light": "grow_light",
        }

        device_name = command_names.get(
            self._device_type,
            self._device_type,
        )

        commands = {
            ActuatorState.OFF: f"power_on_{device_name}",
            ActuatorState.IDLE: f"start_{device_name}",
            ActuatorState.RUNNING: f"stop_{device_name}",
            ActuatorState.MAINTENANCE: f"resume_{device_name}",
            ActuatorState.ERROR: f"reset_{device_name}",
        }

        allowed = [commands[self._state]]

        if (
            device_name == "grow_light"
            and self._state == ActuatorState.RUNNING
        ):
            allowed.append("set_light_level")

        return allowed

    def transition(self, target: str) -> str:
        try:
            target_state = ActuatorState(target)
        except ValueError as exc:
            raise InvalidActuatorTransition(
                f"Unknown actuator state: {target}"
            ) from exc

        if target_state not in ALLOWED_TRANSITIONS[self._state]:
            raise InvalidActuatorTransition(
                f"Transition from {self._state.value} "
                f"to {target_state.value} is not allowed."
            )

        self._state = target_state
        return self._state.value
