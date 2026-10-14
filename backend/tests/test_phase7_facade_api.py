import json
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import UUID

from src.infrastructure.db import SessionLocal
from src.infrastructure.persistence.models import DeviceRow, ReadingRow


BASE_URL = "http://127.0.0.1:8000"


def api_request(path, method="GET", payload=None):
    data = None
    headers = {}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(
        f"{BASE_URL}{path}",
        data=data,
        headers=headers,
        method=method,
    )

    with urlopen(request, timeout=10) as response:
        body = response.read()
        return response.status, json.loads(body) if body else None


def create_test_location():
    name = f"Phase 7 Facade Test {uuid.uuid4().hex[:10]}"

    status, result = api_request(
        "/api/locations/config",
        method="POST",
        payload={
            "location_name": name,
            "zones": [
                {
                    "name": "Facade Test Zone",
                    "moisture_threshold_low": 0.3,
                    "moisture_threshold_high": 0.6,
                    "schedule": {"watering": "08:00"},
                }
            ],
        },
    )

    assert status == 201
    return result["location"]["id"], result["zones"][0]["id"]


def create_test_sensor(sensor_type, display_name):
    status, result = api_request(
        "/api/sensors",
        method="POST",
        payload={
            "type": sensor_type,
            "display_name": display_name,
        },
    )

    assert status == 201
    return result["id"]


def cleanup_test_devices(device_ids):
    if not device_ids:
        return

    parsed_ids = [UUID(device_id) for device_id in device_ids]
    db = SessionLocal()

    try:
        db.query(ReadingRow).filter(
            ReadingRow.device_id.in_(parsed_ids)
        ).delete(synchronize_session=False)

        db.query(DeviceRow).filter(
            DeviceRow.id.in_(parsed_ids)
        ).delete(synchronize_session=False)

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_test_location(location_id):
    try:
        api_request(
            f"/api/locations/{location_id}",
            method="DELETE",
        )
    except HTTPError as error:
        if error.code != 404:
            raise


def test_overview_includes_assigned_devices_latest_readings_and_strategy():
    location_id = None
    test_device_ids = []

    try:
        location_id, zone_id = create_test_location()

        moisture_sensor_id = create_test_sensor(
            "moisture",
            f"Facade Moisture {uuid.uuid4().hex[:8]}",
        )
        test_device_ids.append(moisture_sensor_id)

        unassigned_sensor_id = create_test_sensor(
            "light",
            f"Facade Unassigned {uuid.uuid4().hex[:8]}",
        )
        test_device_ids.append(unassigned_sensor_id)

        status, assigned_device = api_request(
            f"/api/devices/{moisture_sensor_id}/zone",
            method="PATCH",
            payload={"zone_id": zone_id},
        )

        assert status == 200
        assert assigned_device["id"] == moisture_sensor_id

        status, reading = api_request(
            f"/api/sensors/{moisture_sensor_id}/read",
            method="POST",
        )

        assert status == 200

        status, strategy = api_request(
            f"/api/locations/{location_id}/automation",
            method="PUT",
            payload={"strategy_key": "conservative"},
        )

        assert status == 200
        assert strategy["strategy_key"] == "conservative"

        status, overview = api_request(
            f"/api/locations/{location_id}/overview"
        )

        assert status == 200
        assert overview["location"]["id"] == location_id
        assert overview["location"]["name"].startswith(
            "Phase 7 Facade Test "
        )

        # Only devices assigned to zones in this location are counted.
        assert overview["device_counts"]["sensor"] == 1
        assert overview["device_counts"]["actuator"] == 0

        assert len(overview["zones"]) == 1
        zone = overview["zones"][0]
        assert zone["id"] == zone_id

        assert len(zone["devices"]) == 1
        assert zone["devices"][0]["id"] == moisture_sensor_id
        assert zone["devices"][0]["device_type"] == "moisture_sensor"

        # The overview reads the persisted reading, not a new live value.
        assert len(zone["latest_readings"]) == 1
        latest = zone["latest_readings"][0]

        assert latest["device_id"] == moisture_sensor_id
        assert latest["value"] == reading["value"]
        assert latest["unit"] == reading["unit"]
        assert latest["recorded_at"] == reading["recorded_at"]
        assert isinstance(latest["tracking_enabled"], bool)
        assert latest["sampling_interval_seconds"] >= 5

        assert overview["strategy_key"] == "conservative"
        assert overview["last_recommendation"] is not None
        assert overview["last_recommendation"]["action"]
        assert overview["last_recommendation"]["reason"]

    finally:
        try:
            cleanup_test_devices(test_device_ids)
        finally:
            if location_id is not None:
                delete_test_location(location_id)


def test_overview_returns_404_for_missing_location():
    location_id = str(uuid.uuid4())

    try:
        api_request(f"/api/locations/{location_id}/overview")
    except HTTPError as error:
        assert error.code == 404
        body = json.loads(error.read().decode("utf-8"))
        assert "Location not found" in body["detail"]
    else:
        raise AssertionError(
            "Expected HTTP 404 for a missing location"
        )



def test_overview_without_strategy_keeps_empty_zones_and_reuses_evaluation():
    location_id = None

    try:
        name = f"Phase 7 Empty Zone Test {uuid.uuid4().hex[:10]}"

        status, result = api_request(
            "/api/locations/config",
            method="POST",
            payload={
                "location_name": name,
                "zones": [
                    {
                        "name": "Alpha Zone",
                        "moisture_threshold_low": 0.3,
                        "moisture_threshold_high": 0.6,
                        "schedule": {"watering": "08:00"},
                    },
                    {
                        "name": "Beta Zone",
                        "moisture_threshold_low": 0.2,
                        "moisture_threshold_high": 0.5,
                        "schedule": {"watering": "09:00"},
                    },
                ],
            },
        )

        assert status == 201
        location_id = result["location"]["id"]

        # No saved strategy should not prevent the overview from loading.
        status, overview = api_request(
            f"/api/locations/{location_id}/overview"
        )

        assert status == 200
        assert overview["strategy_key"] is None
        assert overview["last_recommendation"] is None
        assert len(overview["zones"]) == 2

        for zone in overview["zones"]:
            assert zone["devices"] == []
            assert zone["latest_readings"] == []

        # Save a strategy and compare the overview with normal evaluation.
        status, saved = api_request(
            f"/api/locations/{location_id}/automation",
            method="PUT",
            payload={"strategy_key": "conservative"},
        )
        assert status == 200
        assert saved["strategy_key"] == "conservative"

        status, evaluation = api_request(
            f"/api/locations/{location_id}/automation/evaluate",
            method="POST",
        )
        assert status == 200
        assert evaluation["recommendations"]

        status, overview = api_request(
            f"/api/locations/{location_id}/overview"
        )
        assert status == 200
        assert overview["strategy_key"] == evaluation["strategy_key"]

        actual = overview["last_recommendation"]
        expected = evaluation["recommendations"][0]

        assert actual["action"] == expected["action"]
        assert actual["reason"] == expected["reason"]

    finally:
        if location_id is not None:
            delete_test_location(location_id)
