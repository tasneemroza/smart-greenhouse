# Adapter Pattern

## Purpose

The Adapter pattern allows different sensor data sources to be converted into the greenhouse application's common `Reading` format.

The application can work with simulation sensors, vendor sensors, and MQTT payloads without changing the reading storage logic.

## SensorPort

`SensorPort` defines the common sensor interface.

Sensor adapters use this interface to produce a domain `Reading`.

## Simulation Adapter

`SimulationSensorAdapter` generates sensor values for simulation devices.

Supported simulation sensors include:

- Moisture sensor: 0.2–0.6 VWC
- Light sensor: 200–2000 lux

The generated reading uses:

```text
source = simulation