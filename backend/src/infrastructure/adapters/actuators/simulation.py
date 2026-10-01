from src.domain.actuators.ports import ActuatorPort


class SimulationActuatorAdapter(ActuatorPort):
    def __init__(self):
        self.state = False

    def set_state(self, state: bool) -> None:
        self.state = bool(state)

    def get_state(self) -> bool:
        return self.state