from abc import ABC, abstractmethod


class ActuatorPort(ABC):
    @abstractmethod
    def set_state(self, state: bool) -> None:
        raise NotImplementedError