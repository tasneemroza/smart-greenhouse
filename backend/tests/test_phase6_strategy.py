from uuid import uuid4

import pytest

from src.domain.automation.entity import LocationAutomationContext
from src.domain.automation.strategies import (
    AggressiveMoistureStrategy,
    ConservativeMoistureStrategy,
    get_strategy,
)


def make_context(moisture=0.4):
    return LocationAutomationContext(
        location_id=uuid4(),
        zone_id=uuid4(),
        latest_moisture=moisture,
        latest_light=800.0,
        moisture_threshold_low=0.3,
        moisture_threshold_high=0.6,
    )


def test_conservative_waits_when_within_band():
    context = make_context(moisture=0.4)

    recommendation = ConservativeMoistureStrategy().decide(context)

    assert recommendation.action == "wait"


def test_aggressive_differs_on_same_context():
    context = make_context(moisture=0.4)

    conservative = ConservativeMoistureStrategy().decide(context)
    aggressive = AggressiveMoistureStrategy().decide(context)

    assert conservative.action == "wait"
    assert aggressive.action == "water"


def test_missing_moisture_reading_returns_wait():
    recommendation = get_strategy("conservative").decide(
        make_context(moisture=None)
    )

    assert recommendation.action == "wait"
    assert "No moisture reading" in recommendation.reason


def test_unknown_strategy_is_rejected():
    with pytest.raises(ValueError, match="Unknown automation strategy"):
        get_strategy("unknown")
