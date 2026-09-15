# Factory Method Pattern

## Purpose

The Smart Greenhouse project uses the Factory Method pattern to create different types of sensors.

The main idea is that the application does not directly create `MoistureSensor` or `LightSensor` objects. Instead, it uses a creator interface and specific creator classes.

## Creator Interface

The `SensorCreator` class defines the method:

```python
create_sensor()