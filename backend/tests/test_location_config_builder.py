import pytest

from src.domain.locations.config_builder import LocationConfigBuilder
from src.domain.locations.errors import ConfigurationError


def test_build_success():
    config = (
        LocationConfigBuilder()
        .with_location_name("Lab Site A")
        .add_zone(
            name="North Zone",
            moisture_threshold_low=0.2,
            moisture_threshold_high=0.45,
            schedule={"watering": "08:00"},
        )
        .build()
    )

    assert config.location.name == "Lab Site A"
    assert len(config.location.zones) == 1
    assert config.location.zones[0].name == "North Zone"
    assert config.location.zones[0].moisture_threshold_low == 0.2
    assert config.location.zones[0].moisture_threshold_high == 0.45


def test_build_requires_name():
    builder = LocationConfigBuilder().add_zone(
        name="North Zone",
        moisture_threshold_low=0.2,
        moisture_threshold_high=0.45,
    )

    with pytest.raises(ConfigurationError):
        builder.build()


def test_build_requires_zones():
    builder = LocationConfigBuilder().with_location_name("Lab Site A")

    with pytest.raises(ConfigurationError):
        builder.build()


def test_build_rejects_invalid_thresholds():
    builder = (
        LocationConfigBuilder()
        .with_location_name("Lab Site A")
        .add_zone(
            name="North Zone",
            moisture_threshold_low=0.8,
            moisture_threshold_high=0.4,
        )
    )

    with pytest.raises(ConfigurationError):
        builder.build()


def test_build_rejects_threshold_out_of_range():
    builder = (
        LocationConfigBuilder()
        .with_location_name("Lab Site A")
        .add_zone(
            name="North Zone",
            moisture_threshold_low=-0.1,
            moisture_threshold_high=0.4,
        )
    )

    with pytest.raises(ConfigurationError):
        builder.build()