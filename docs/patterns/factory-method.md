# Factory Method Pattern

## Problem

The Smart Greenhouse needs to create different types of sensors, such as moisture and light sensors. If the API directly creates each sensor type, the code can become harder to maintain when new sensor types are added.

## Solution

The project uses the **Factory Method pattern** to create sensors.

The API and application service do not directly create `MoistureSensor` or `LightSensor` objects. Instead, the `SensorService` asks `get_creator()` for the correct creator. The creator then creates the sensor with its own default configuration.

The main creator interface is:

```python
class SensorCreator(ABC):
    @abstractmethod
    def create_sensor(self, display_name: str | None = None) -> Sensor:
        ...
```

The project has two concrete creators:

* `MoistureSensorCreator`
* `LightSensorCreator`

The `get_creator()` function selects the correct creator using the sensor type:

```text
"moisture" → MoistureSensorCreator
"light"    → LightSensorCreator
```

An unknown sensor type raises a `ValueError`.

## Sensor Defaults

### Moisture Sensor

The moisture sensor uses:

```text
device_type: moisture_sensor
unit: vwc
threshold: 40
sampling_interval_seconds: 300
```

### Light Sensor

The light sensor uses:

```text
device_type: light_sensor
unit: lux
threshold: 500
sampling_interval_seconds: 300
```

The two sensor types have different configurations, so the Factory Method allows each creator to provide the correct defaults.

## Persistence

Created sensors are stored in the PostgreSQL `devices` table.

The repository is responsible for saving and loading sensors:

```text
backend/src/infrastructure/persistence/device_repository.py
```

The application service uses the repository:

```text
backend/src/application/sensors/service.py
```

## REST API

The sensor API is located at:

```text
backend/src/interfaces/api/sensors.py
```

The API provides:

```text
GET  /api/sensors
POST /api/sensors
```

A POST request can create either a moisture or light sensor.

Example:

```json
{
  "type": "moisture",
  "display_name": "Soil moisture sensor"
}
```

The API returns the created sensor with its generated UUID and default configuration.

## Important Code Paths

```text
backend/src/domain/sensors/entity.py
backend/src/domain/sensors/creators.py
backend/src/application/sensors/service.py
backend/src/infrastructure/persistence/models.py
backend/src/infrastructure/persistence/device_repository.py
backend/src/interfaces/api/sensors.py
frontend/src/services/api.ts
frontend/src/features/sensors/SensorList.tsx
```

## Why Factory Method?

The main benefit is that the application does not need to know how every sensor type is created.

If a new sensor type is added later, a new creator can provide its own type and default configuration without putting all creation logic inside the API endpoint.

This makes the code easier to extend and keeps the creation logic separated from the rest of the application.

## Exercise: Temperature Sensor

As an exercise, a `TemperatureSensorCreator` could be added.

It could create a sensor with:

```text
device_type: temperature_sensor
unit: celsius
threshold: 25
sampling_interval_seconds: 300
```

The creator would implement the same `SensorCreator` interface:

```python
class TemperatureSensorCreator(SensorCreator):
    def create_sensor(self, display_name: str | None = None) -> Sensor:
        ...
```

Then `"temperature"` could be added to the creator registry in `creators.py`.

This would allow the application to create temperature sensors without changing the basic Factory Method structure.
