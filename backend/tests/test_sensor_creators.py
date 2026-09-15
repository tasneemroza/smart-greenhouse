from src.domain.sensors.creators import (
    LightSensorCreator,
    MoistureSensorCreator,
)


def test_moisture_sensor_creator():
    creator = MoistureSensorCreator()

    sensor = creator.create_sensor()

    assert sensor.device_type == "moisture"
    assert sensor.display_name == "Moisture Sensor"
    assert sensor.default_config == {
        "threshold": 40,
        "unit": "percent",
    }


def test_light_sensor_creator():
    creator = LightSensorCreator()

    sensor = creator.create_sensor()

    assert sensor.device_type == "light"
    assert sensor.display_name == "Light Sensor"
    assert sensor.default_config == {
        "threshold": 500,
        "unit": "lux",
    }


def test_custom_display_name():
    creator = MoistureSensorCreator()

    sensor = creator.create_sensor("My Greenhouse Sensor")

    assert sensor.display_name == "My Greenhouse Sensor"