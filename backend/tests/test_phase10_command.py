from uuid import uuid4

import pytest

from src.domain.commands.invoker import (
    COMMAND_REGISTRY,
    CommandInvoker,
    command_for,
)
from src.infrastructure.adapters.actuators.simulation import (
    SimulationActuatorAdapter,
)


@pytest.mark.parametrize(
    "command_type",
    [
        "start_pump",
        "stop_pump",
        "start_grow_light",
        "stop_grow_light",
        "set_light_level",
    ],
)
def test_command_is_registered(command_type):
    assert command_type in COMMAND_REGISTRY


@pytest.mark.parametrize(
    "command_type,expected_state",
    [
        ("start_pump", "running"),
        ("stop_pump", "idle"),
        ("start_grow_light", "running"),
        ("stop_grow_light", "idle"),
    ],
)
def test_command_executes_and_has_correct_target_state(
    command_type,
    expected_state,
):
    device_id = uuid4()
    simulation = SimulationActuatorAdapter()

    command = command_for(command_type, device_id, {})
    CommandInvoker().run(command, simulation)

    assert command.target_state == expected_state
    assert len(simulation.commands) == 1


def test_light_level_command_executes():
    device_id = uuid4()
    simulation = SimulationActuatorAdapter()

    command = command_for(
        "set_light_level",
        device_id,
        {"level": 50},
    )

    CommandInvoker().run(command, simulation)

    assert command.target_state is None
    assert command.payload["level"] == 50
    assert len(simulation.commands) == 1


@pytest.mark.parametrize("level", [-1, 101, "high", True])
def test_invalid_light_level_is_rejected(level):
    simulation = SimulationActuatorAdapter()
    command = command_for(
        "set_light_level",
        uuid4(),
        {"level": level},
    )

    with pytest.raises(ValueError):
        CommandInvoker().run(command, simulation)

    assert len(simulation.commands) == 0


def test_unknown_command_is_rejected():
    with pytest.raises(ValueError, match="Unknown command type"):
        command_for("unknown_command", uuid4(), {})


def test_command_invoker_passes_device_id_and_payload():
    device_id = uuid4()
    simulation = SimulationActuatorAdapter()

    command = command_for(
        "start_pump",
        device_id,
        {"duration": 30},
    )

    CommandInvoker().run(command, simulation)

    assert len(simulation.commands) == 1
