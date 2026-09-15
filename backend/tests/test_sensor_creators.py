from src.domain.sensors.creators import (
    LightSensorCreator,
    MoistureSensorCreator,
)


def test_moisture_creator_defaults():
    creator = MoistureSensorCreator()
    sensor = creator.create_sensor()

    assert sensor.device_type == "moisture_sensor"
    assert sensor.display_name == "Moisture Sensor"
    assert sensor.default_config["unit"] == "vwc"
    assert "threshold" in sensor.default_config
    assert sensor.default_config["sampling_interval_seconds"] == 300


def test_light_creator_defaults():
    creator = LightSensorCreator()
    sensor = creator.create_sensor()

    assert sensor.device_type == "light_sensor"
    assert sensor.display_name == "Light Sensor"
    assert sensor.default_config["unit"] == "lux"
    assert sensor.default_config["sampling_interval_seconds"] == 300


def test_custom_display_name():
    creator = MoistureSensorCreator()
    sensor = creator.create_sensor("My Greenhouse Sensor")

    assert sensor.display_name == "My Greenhouse Sensor"