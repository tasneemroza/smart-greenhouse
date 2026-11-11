from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from src.infrastructure.adapters.actuators.logging_decorator import (
    LoggingActuatorDecorator,
)
from src.infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRunTimeActuatorDecorator,
    MaxRunTimeExceededError,
)
from src.infrastructure.adapters.actuators.simulation import (
    SimulationActuatorAdapter,
)


NOW = datetime(2026, 11, 11, 12, 0, tzinfo=timezone.utc)


class FakeStateRepository:
    def __init__(self, state="idle", minutes_ago=0):
        self.state = SimpleNamespace(
            state=state,
            updated_at=NOW - timedelta(minutes=minutes_ago),
        )

    def get_state(self, device_id):
        return self.state


class FakeExecutionLogRepository:
    def __init__(self):
        self.records = []

    def create(self, **kwargs):
        self.records.append(kwargs)


def build_actuator(state="idle", minutes_ago=0):
    simulation = SimulationActuatorAdapter()
    states = FakeStateRepository(state, minutes_ago)
    logs = FakeExecutionLogRepository()

    runtime = MaxRunTimeActuatorDecorator(
        inner=simulation,
        state_repository=states,
        clock=lambda: NOW,
    )

    actuator = LoggingActuatorDecorator(
        inner=runtime,
        log_repository=logs,
    )

    return actuator, simulation, logs


def test_successful_command_is_logged():
    actuator, simulation, logs = build_actuator()
    device_id = uuid4()

    actuator.apply(device_id, "turn_on", {"duration": 60})

    assert len(simulation.commands) == 1
    assert len(logs.records) == 1
    assert logs.records[0]["device_id"] == device_id
    assert logs.records[0]["success"] is True
    assert logs.records[0]["policy_applied"] == ["logging"]
    assert logs.records[0]["message"] is None


def test_unknown_command_is_forwarded_without_validation():
    actuator, simulation, logs = build_actuator()
    device_id = uuid4()

    actuator.apply(device_id, "unknown_command", {})

    assert len(simulation.commands) == 1
    assert logs.records[0]["success"] is True


def test_running_actuator_before_limit_is_allowed():
    actuator, simulation, logs = build_actuator(
        state="running",
        minutes_ago=29,
    )

    actuator.apply(uuid4(), "turn_on", {})

    assert len(simulation.commands) == 1
    assert logs.records[0]["success"] is True


@pytest.mark.parametrize("minutes_ago", [30, 31, 60])
def test_max_runtime_blocks_and_logs_failure(minutes_ago):
    actuator, simulation, logs = build_actuator(
        state="running",
        minutes_ago=minutes_ago,
    )

    with pytest.raises(
        MaxRunTimeExceededError,
        match="Max run time exceeded",
    ):
        actuator.apply(uuid4(), "turn_on", {})

    assert len(simulation.commands) == 0
    assert len(logs.records) == 1
    assert logs.records[0]["success"] is False
    assert logs.records[0]["policy_applied"] == [
        "maxRunTime",
        "logging",
    ]
    assert logs.records[0]["message"] == "Max run time exceeded"


def test_idle_actuator_is_not_blocked_by_old_timestamp():
    actuator, simulation, logs = build_actuator(
        state="idle",
        minutes_ago=120,
    )

    actuator.apply(uuid4(), "turn_on", {})

    assert len(simulation.commands) == 1
    assert logs.records[0]["success"] is True
