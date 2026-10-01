from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.domain.sensors.reading import Reading
from src.infrastructure.adapters.sensors.mqtt import MqttSensorAdapter
from src.infrastructure.adapters.sensors.simulation import (
    SimulationSensorAdapter,
)
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
    assert 0.2 <= reading.value <= 0.6
    assert reading.unit == "vwc"
    assert reading.source == "simulation"


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
    assert 200.0 <= reading.value <= 2000.0
    assert reading.unit == "lux"
    assert reading.source == "simulation"


def test_vendor_adapter_normalizes_value_and_unit():
    device_id = uuid4()

    adapter = VendorSensorAdapter(
        device_id=device_id,
        unit="vwc",
    )

    timestamp = datetime(
        2026,
        9,
        29,
        11,
        0,
        tzinfo=timezone.utc,
    )

    reading = adapter.read(
        raw_value="0.45",
        raw_unit="vwc",
        timestamp=timestamp,
    )

    assert isinstance(reading, Reading)
    assert reading.device_id == device_id
    assert reading.value == 0.45
    assert reading.unit == "vwc"
    assert reading.source == "vendor"
    assert reading.recorded_at == timestamp


def test_mqtt_adapter_translates_payload():
    device_id = uuid4()

    adapter = MqttSensorAdapter(
        device_id=device_id,
        unit="lux",
    )

    timestamp = datetime(
        2026,
        9,
        29,
        12,
        0,
        tzinfo=timezone.utc,
    )

    reading = adapter.translate(
        {
            "value": 850,
            "unit": "lux",
            "recorded_at": timestamp.isoformat(),
        }
    )

    assert reading.device_id == device_id
    assert reading.value == 850.0
    assert reading.unit == "lux"
    assert reading.source == "mqtt"
    assert reading.recorded_at == timestamp


def test_mqtt_adapter_requires_value():
    device_id = uuid4()

    adapter = MqttSensorAdapter(
        device_id=device_id,
        unit="lux",
    )

    with pytest.raises(ValueError, match="missing value"):
        adapter.translate(
            {
                "unit": "lux",
            }
        )


def test_mqtt_adapter_read_requires_payload():
    device_id = uuid4()

    adapter = MqttSensorAdapter(
        device_id=device_id,
        unit="lux",
    )

    with pytest.raises(
        RuntimeError,
        match="inbound payload",
    ):
        adapter.read()