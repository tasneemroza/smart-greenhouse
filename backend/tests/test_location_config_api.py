import json
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen


BASE_URL = "http://127.0.0.1:8000"


def test_create_and_get_location_config():
    payload = {
        "location_name": "API Test Greenhouse",
        "zones": [
            {
                "name": "North Zone",
                "moisture_threshold_low": 0.2,
                "moisture_threshold_high": 0.45,
                "schedule": {"watering": "08:00"},
            },
            {
                "name": "South Zone",
                "moisture_threshold_low": 0.25,
                "moisture_threshold_high": 0.5,
                "schedule": {"watering": "09:00"},
            },
        ],
    }

    request = Request(
        f"{BASE_URL}/api/locations/config",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=10) as response:
        assert response.status == 201
        created = json.load(response)

    assert created["location"]["name"] == "API Test Greenhouse"
    assert len(created["zones"]) == 2

    location_id = created["location"]["id"]
    uuid.UUID(location_id)

    for zone in created["zones"]:
        assert zone["location_id"] == location_id

    with urlopen(
        f"{BASE_URL}/api/locations/{location_id}/config",
        timeout=10,
    ) as response:
        assert response.status == 200
        saved = json.load(response)

    assert saved["location"]["id"] == location_id
    assert saved["location"]["name"] == "API Test Greenhouse"
    assert len(saved["zones"]) == 2
    assert all(
        zone["location_id"] == location_id
        for zone in saved["zones"]
    )


def test_get_missing_location_returns_404():
    location_id = "00000000-0000-0000-0000-000000000000"

    try:
        urlopen(
            f"{BASE_URL}/api/locations/{location_id}/config",
            timeout=10,
        )
    except HTTPError as error:
        assert error.code == 404
    else:
        raise AssertionError("Expected 404 for missing location")
def test_invalid_threshold_payload_returns_400():
    payload = {
        "location_name": "Invalid API Test",
        "zones": [
            {
                "name": "Invalid Zone",
                "moisture_threshold_low": 0.8,
                "moisture_threshold_high": 0.4,
                "schedule": {"watering": "08:00"},
            }
        ],
    }

    request = Request(
        f"{BASE_URL}/api/locations/config",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        urlopen(request, timeout=10)
    except HTTPError as error:
        assert error.code == 400
        response_body = json.loads(error.read().decode("utf-8"))
        assert "Low moisture threshold must be lower than high threshold." in response_body["detail"]
    else:
        raise AssertionError("Expected 400 for invalid threshold configuration")