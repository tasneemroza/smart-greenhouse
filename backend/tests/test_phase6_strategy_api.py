import json
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen

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
    name = f"Phase 6 API Test {uuid.uuid4().hex[:10]}"

    status, result = api_request(
        "/api/locations/config",
        method="POST",
        payload={
            "location_name": name,
            "zones": [
                {
                    "name": "Test Zone",
                    "moisture_threshold_low": 0.3,
                    "moisture_threshold_high": 0.6,
                    "schedule": {"watering": "08:00"},
                }
            ],
        },
    )

    assert status == 201
    return result["location"]["id"]


def delete_test_location(location_id):
    try:
        api_request(
            f"/api/locations/{location_id}",
            method="DELETE",
        )
    except HTTPError as error:
        if error.code != 404:
            raise


def test_save_and_evaluate_persisted_strategy():
    location_id = create_test_location()

    try:
        status, saved = api_request(
            f"/api/locations/{location_id}/automation",
            method="PUT",
            payload={"strategy_key": "conservative"},
        )

        assert status == 200
        assert saved["location_id"] == location_id
        assert saved["strategy_key"] == "conservative"
        assert saved["updated_at"]

        status, result = api_request(
            f"/api/locations/{location_id}/automation/evaluate",
            method="POST",
        )

        assert status == 200
        assert result["location_id"] == location_id
        assert result["strategy_key"] == "conservative"
        assert len(result["recommendations"]) == 1

        recommendation = result["recommendations"][0]
        assert recommendation["action"] == "wait"
        assert "No moisture sensor" in recommendation["reason"]

        _, saved_again = api_request(
            f"/api/locations/{location_id}/automation",
            method="PUT",
            payload={"strategy_key": "aggressive"},
        )

        assert saved_again["strategy_key"] == "aggressive"

        _, reevaluated = api_request(
            f"/api/locations/{location_id}/automation/evaluate",
            method="POST",
        )

        assert reevaluated["strategy_key"] == "aggressive"
    finally:
        delete_test_location(location_id)


def test_unknown_strategy_returns_400():
    location_id = create_test_location()

    try:
        try:
            api_request(
                f"/api/locations/{location_id}/automation",
                method="PUT",
                payload={"strategy_key": "unknown"},
            )
        except HTTPError as error:
            assert error.code == 400
            body = json.loads(error.read().decode("utf-8"))
            assert "Unknown automation strategy" in body["detail"]
        else:
            raise AssertionError("Expected HTTP 400 for unknown strategy")
    finally:
        delete_test_location(location_id)


def test_missing_location_returns_404():
    location_id = "00000000-0000-0000-0000-000000000000"

    try:
        api_request(
            f"/api/locations/{location_id}/automation",
            method="PUT",
            payload={"strategy_key": "conservative"},
        )
    except HTTPError as error:
        assert error.code == 404
    else:
        raise AssertionError("Expected HTTP 404 for missing location")


def test_evaluation_without_saved_strategy_returns_400():
    location_id = create_test_location()

    try:
        try:
            api_request(
                f"/api/locations/{location_id}/automation/evaluate",
                method="POST",
            )
        except HTTPError as error:
            assert error.code == 400
            body = json.loads(error.read().decode("utf-8"))
            assert "No automation strategy configured" in body["detail"]
        else:
            raise AssertionError(
                "Expected HTTP 400 when no strategy is configured"
            )
    finally:
        delete_test_location(location_id)
