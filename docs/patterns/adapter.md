# Adapter Pattern

## Purpose

The Adapter pattern converts data from different sensor sources into the greenhouse application's common `Reading` format. This lets the application share reading-ingestion and persistence logic.

## Common interface

File: `backend/src/domain/sensors/ports.py`

`SensorPort` defines a `read()` operation that returns a domain `Reading`.

The reading contains:

- `device_id`
- `value`
- `unit`
- `source`
- `recorded_at`

The timestamp must be timezone-aware. The allowed sources are `simulation`, `mqtt`, and `vendor`.

## SimulationSensorAdapter

File: `backend/src/infrastructure/adapters/sensors/simulation.py`

The simulation adapter generates readings for supported simulation sensors.

Expected value ranges:

- Moisture: 0.2–0.6 VWC
- Light: 200–2000 lux

The source is recorded as `simulation`.

## VendorSensorAdapter

File: `backend/src/infrastructure/adapters/sensors/vendor_stub.py`

The vendor adapter converts a supplied value to a floating-point number and uses the supplied unit or its configured default.

The source is recorded as `vendor`. This is a course-project stub, not a complete real vendor integration.

## MqttSensorAdapter

File: `backend/src/infrastructure/adapters/sensors/mqtt.py`

The MQTT adapter translates an inbound payload into a `Reading`. The payload must contain `value` and may include `unit` and `recorded_at`.

If the unit or timestamp is missing, the adapter uses its configured unit or the current UTC time. The source is recorded as `mqtt`.

This adapter does not establish a live MQTT connection. Its `read()` method requires an inbound payload, and `translate()` performs the conversion.

## ReadingIngest

File: `backend/src/application/sensors/reading_ingest.py`

`ReadingIngest` checks that the device exists and has the sensor role, creates or receives a reading, and sends it to the repository for storage. It also supports listing a device's reading history.

For a manual reading, it selects an adapter according to the device configuration. MQTT devices require an inbound payload and cannot use the ordinary manual-read path to create a reading.

Using one ingestion service avoids duplicating persistence logic across sensor sources.

## SimulationSampler

File: `backend/src/application/sensors/simulation_sampler.py`

`SimulationSampler` checks eligible simulation-family sensors and records readings when their sampling intervals have elapsed.

It skips devices that are not eligible for simulation sampling and those that do not yet need another reading. Eligible readings go through `ReadingIngest`, so the sampler does not implement a separate storage path.

## Reading history

- Domain model: `backend/src/domain/sensors/reading.py`
- Repository: `backend/src/infrastructure/persistence/reading_repository.py`

Readings are stored as history so previous measurements can be retrieved instead of overwriting a single latest-value record.

## Tests

File: `backend/tests/test_phase5_adapter.py`

The tests cover simulated moisture and light ranges, vendor value and unit conversion, MQTT payload translation, missing MQTT values, and the requirement for an inbound MQTT payload.

Run them with:

```powershell
docker compose exec backend pytest tests/test_phase5_adapter.py -q
```

## Why use the Adapter pattern?

Each source can translate its data into the same domain format. The application can then share its reading-ingestion and persistence logic rather than implementing separate storage behavior for each source.

A real vendor connection or MQTT broker integration could be added later while keeping the common reading model.