from types import SimpleNamespace
from uuid import uuid4

import pytest

from src.application.devices.actuator_state_service import (
    ActuatorStateService,
)
from src.domain.actuators.state import (
    ALLOWED_TRANSITIONS,
    ActuatorContext,
    ActuatorState,
    InvalidActuatorTransition,
)


LEGAL_TRANSITIONS = [
    ("off", "idle"),
    ("off", "error"),
    ("idle", "running"),
    ("idle", "off"),
    ("idle", "maintenance"),
    ("idle", "error"),
    ("running", "idle"),
    ("running", "maintenance"),
    ("running", "error"),
    ("maintenance", "idle"),
    ("maintenance", "off"),
    ("maintenance", "error"),
    ("error", "idle"),
]


@pytest.mark.parametrize(("current", "target"), LEGAL_TRANSITIONS)
def test_legal_transitions(current, target):
    context = ActuatorContext(current, "water_pump")

    assert context.transition(target) == target
    assert context.state == target


def test_all_other_transitions_are_rejected():
    for current in ActuatorState:
        for target in ActuatorState:
            if target not in ALLOWED_TRANSITIONS[current]:
                context = ActuatorContext(
                    current.value,
                    "water_pump",
                )

                with pytest.raises(InvalidActuatorTransition):
                    context.transition(target.value)

                assert context.state == current.value


def test_unknown_state_transition_is_rejected():
    context = ActuatorContext("idle", "water_pump")

    with pytest.raises(InvalidActuatorTransition):
        context.transition("unknown")

    assert context.state == "idle"


@pytest.mark.parametrize(
    ("state", "expected_command"),
    [
        ("off", "power_on_pump"),
        ("idle", "start_pump"),
        ("running", "stop_pump"),
        ("maintenance", "resume_pump"),
        ("error", "reset_pump"),
    ],
)
def test_allowed_commands_match_state(state, expected_command):
    context = ActuatorContext(state, "water_pump")

    assert context.allowed_commands() == [expected_command]


def test_grow_light_commands_use_grow_light_name():
    context = ActuatorContext("idle", "grow_light")

    assert context.allowed_commands() == ["start_grow_light"]


class FakeActuatorStateRepository:
    def __init__(self, state):
        self.device_id = uuid4()
        self.device = SimpleNamespace(
            id=self.device_id,
            device_type="water_pump",
        )
        self.state_row = SimpleNamespace(
            device_id=self.device_id,
            state=state,
            updated_at=None,
        )
        self.save_count = 0
        self.rollback_count = 0

    def get_actuator(self, device_id):
        if device_id == self.device_id:
            return self.device
        return None

    def get_state(self, device_id):
        if device_id == self.device_id:
            return self.state_row
        return None

    def get_state_for_update(self, device_id):
        if device_id == self.device_id:
            return self.state_row
        return None

    def save(self, state):
        self.save_count += 1
        return state

    def rollback(self):
        self.rollback_count += 1


def test_service_saves_a_legal_transition():
    repository = FakeActuatorStateRepository("idle")
    service = ActuatorStateService(repository)

    result = service.transition(
        repository.device_id,
        "running",
    )

    assert result.state == "running"
    assert result.allowed_commands == ["stop_pump"]
    assert repository.state_row.state == "running"
    assert repository.save_count == 1
    assert repository.rollback_count == 0


def test_service_does_not_save_an_illegal_transition():
    repository = FakeActuatorStateRepository("off")
    service = ActuatorStateService(repository)

    with pytest.raises(InvalidActuatorTransition):
        service.transition(
            repository.device_id,
            "running",
        )

    assert repository.state_row.state == "off"
    assert repository.save_count == 0
    assert repository.rollback_count == 1
