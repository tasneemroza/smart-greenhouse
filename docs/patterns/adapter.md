# Adapter Pattern

## Problem

The Smart Greenhouse application can receive sensor data from different sources. Simulation sensors generate values inside the application, while MQTT and vendor devices can provide data in different formats.

If the application had to understand every sensor format directly, the application logic would become dependent on specific devices and protocols. This would make it harder to add new sensor vendors or change the way sensor data is received.

## Solution

The Adapter pattern gives the application one common interface for reading sensor data.

The domain defines the `SensorPort` interface and the immutable `Reading` model. Infrastructure adapters implement the interface and translate different sensor sources into the common `Reading` format.

The current adapters are:

* `SimulationSensorAdapter` generates simulated sensor values.
* `MqttSensorAdapter` translates an inbound MQTT payload into a `Reading`.
* `VendorSensorAdapter` translates vendor-specific sensor data into a `Reading`.

`ReadingIngest` is the common application path for storing successful readings. It receives a normalized `Reading` and persists it through `ReadingRepository`.

This keeps the domain and application logic independent from the specific sensor source.

## Where the Pattern Lives

The main domain port is located at:

`backend/src/domain/sensors/ports.py`

The common reading model is located at:

`backend/src/domain/sensors/reading.py`

The sensor adapters are located at:

`backend/src/infrastructure/adapters/sensors/`

The current adapter implementations are:

* `simulation.py`
* `mqtt.py`
* `vendor_stub.py`

The common persistence path is implemented in:

`backend/src/application/sensors/reading_ingest.py`

The database persistence is handled by:

`backend/src/infrastructure/persistence/reading_repository.py`

## Adding Another Vendor

To add another sensor vendor:

1. Create a new adapter in `backend/src/infrastructure/adapters/sensors/`.
2. Implement the sensor translation using the common `SensorPort` interface.
3. Convert the vendor's raw data into the domain `Reading` model.
4. Set the correct reading source, such as `vendor`.
5. Add the vendor protocol to the adapter selection logic in `ReadingIngest`.
6. Add tests for the new adapter's raw-data translation.
7. Verify that the resulting reading is stored through the existing `ReadingIngest.record()` path.

The existing domain and database model do not need to be changed just because a new vendor is added.

## Benefit

The Adapter pattern separates sensor-specific data formats from the rest of the Smart Greenhouse application. The application can work with the same `Reading` model regardless of whether the data comes from simulation, MQTT, or a vendor device.
