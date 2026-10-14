# Facade Pattern — Phase 7

## Purpose

The Facade Pattern provides one simple interface to a group of underlying
services and data sources. A caller uses the facade instead of coordinating
those components directly.

## Application in Smart Greenhouse

`LocationOverviewFacade` provides the overview for one greenhouse location.

Its main method is:

`get_overview(location_id: UUID)`

The API endpoint is:

`GET /api/locations/{location_id}/overview`

The router injects `LocationOverviewFacade` and delegates the overview
request to it. If the location does not exist, the endpoint returns HTTP 404.

## Responsibilities

The facade gathers the data needed by the overview:

- Location name and ID.
- Sensor and actuator counts for devices assigned to zones in that location.
- Zones, their moisture thresholds, and their assigned devices.
- The latest persisted reading for each device that has a reading.
- The configured automation strategy, if one exists.
- A recommendation calculated using the configured strategy, if available.

Devices that are not assigned to a zone in the requested location are
excluded from its device lists and counts.

## Reading retrieval

Readings are retrieved from the persisted `sensor_readings` table.
The facade uses a database window function to select the latest reading
per device in one readings query, rather than issuing a separate readings
query for every device.

A device without a persisted reading has no entry in `latest_readings`.
The reading DTO also includes tracking status and the configured sampling
interval.

## Automation information

The facade reuses the existing automation repository and service.
It does not implement a separate automation strategy or sampler.

`strategy_key` is the saved strategy key, or `null` when no strategy is
configured.

`last_recommendation` represents the recommendation calculated when the
overview is requested. It is not a stored historical recommendation because
this phase does not introduce a recommendation-history table.

## Response structure

The overview response contains:

- `location`
- `device_counts`
- `zones`
- `strategy_key`
- `last_recommendation`

Each zone contains its ID, name, moisture thresholds, assigned devices,
and latest persisted readings.

## Benefits

- The frontend makes one request to load the overview.
- The router remains small and delegates application work to the facade.
- Existing automation and reading services are reused.
- The frontend receives a single structured response.
- Latest-reading retrieval avoids an N+1 readings-query pattern.

## Scope

This phase adds the overview endpoint, its DTOs, the application facade,
frontend overview integration, tests, and this documentation.

It does not add a scheduler, MQTT client, SQL view, database migration,
or a new API for collecting readings.
