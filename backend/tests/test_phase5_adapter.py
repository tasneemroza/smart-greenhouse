from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.infrastructure.adapters.sensors.mqtt import MqttSensorAdapter
from src.infrastructure.adapters.sensors.simulation import SimulationSensorAdapter
from src.infrastructure.adapters.sensors.vendor_stub import VendorSensorAdapter


def test_simulation_moisture_reading_is_in_range():
    device_id = uuid4()
    adapter = SimulationSensorAdapter(
        device_id=device_id,
        device_type="moisture_sensor",
        unit="vwc",
    )

    reading = adapter.read(
        datetime(2026, 9, 29, 10, 0, tzinfo=timezone.utc)
    )

    assert reading.device_id == device_id
    assert 30.0 <= reading.value <= 70.0
    assert reading.unit == "vwc"
    assert reading.source == "simulation"
    assert reading.recorded_at.tzinfo is not None


def test_simulation_light_reading_is_in_range():
    device_id = uuid4()
    adapter = SimulationSensorAdapter(
        device_id=device_id,
        device_type="light_sensor",
        unit="lux",
    )

    reading = adapter.read(
        datetime(2026, 9, 29, 10, 0, tzinfo=timezone.utc)
    )

    assert reading.device_id == device_id
    assert 100.0 <= reading.value <= 1000.0
    assert reading.unit == "lux"
    assert reading.source == "simulation"


def test_vendor_adapter_normalizes_raw_value():
    device_id = uuid4()
    timestamp = datetime(
        2026,
        9,
        29,
        10,
        0,
        tzinfo=timezone.utc,
    )

    adapter = VendorSensorAdapter(
        device_id=device_id,
        unit="percent",
    )

    reading = adapter.read(
        raw_value=58.2,
        raw_unit="percent",
        timestamp=timestamp,
    )

    assert reading.device_id == device_id
    assert reading.value == 58.2
    assert reading.unit == "percent"
    assert reading.source == "vendor"
    assert reading.recorded_at == timestamp


def test_mqtt_adapter_translates_payload_without_broker():
    device_id = uuid4()
    timestamp = datetime(
        2026,
        9,
        29,
        10,
        0,
        tzinfo=timezone.utc,
    )

    adapter = MqttSensorAdapter(
        device_id=device_id,
        unit="vwc",
    )

    reading = adapter.translate(
        {
            "value": 55.5,
            "unit": "vwc",
            "recorded_at": timestamp.isoformat(),
        }
    )

    assert reading.device_id == device_id
    assert reading.value == 55.5
    assert reading.unit == "vwc"
    assert reading.source == "mqtt"
    assert reading.recorded_at == timestamp


def test_mqtt_adapter_rejects_missing_value():
    adapter = MqttSensorAdapter(
        device_id=uuid4(),
        unit="vwc",
    )

    with pytest.raises(
        ValueError,
        match="MQTT payload is missing value",
    ):
        adapter.translate(
            {
                "unit": "vwc",
            }
        )


def test_mqtt_adapter_uses_default_unit():
    device_id = uuid4()

    adapter = MqttSensorAdapter(
        device_id=device_id,
        unit="vwc",
    )

    reading = adapter.translate(
        {
            "value": 42.5,
        }
    )

    assert reading.value == 42.5
    assert reading.unit == "vwc"
    assert reading.source == "mqtt"