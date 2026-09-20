# Abstract Factory

## Problem

The Smart Greenhouse needs different families of devices. For example, simulation devices can use simulated communication, while edge devices can use GPIO-based hardware settings.

Creating these devices directly in different parts of the application could make the code harder to maintain.

## Solution

The Abstract Factory pattern creates a complete family of related devices.

The project has two device families:

- `simulation`
- `edge`

Each family creates four devices:

- moisture sensor
- light sensor
- water pump
- grow light

The `SimulationDeviceFactory` uses simulation configuration, while the `EdgeHardwareFactory` uses edge hardware configuration.

## Factory Method and Abstract Factory

The Phase 2 Factory Method creates individual sensor types such as moisture and light sensors.

The Phase 3 Abstract Factory builds a complete device family. It reuses the Phase 2 sensor creators when creating the sensor part of the family.

This means the Factory Method handles individual product creation, while the Abstract Factory handles a related group of products.

## Code Locations

The main Abstract Factory code is located in:

- `backend/src/domain/devices/entity.py`
- `backend/src/domain/devices/family_factory.py`

The Phase 2 Factory Method creators are located in:

- `backend/src/domain/sensors/creators.py`

The repository is located in:

- `backend/src/infrastructure/persistence/device_repository.py`

The DTO and mapping code is located in:

- `backend/src/application/devices/dto.py`
- `backend/src/application/devices/mappers.py`

The REST API is located in:

- `backend/src/interfaces/api/devices.py`

The frontend components are located in:

- `frontend/src/components/devices/DeviceFamilySwitcher.tsx`
- `frontend/src/components/devices/DeviceList.tsx`

## Why Device Is Different From DTO

The domain `Device` represents the device inside the business logic.

The `DeviceDto` represents the data sent through the REST API.

Keeping them separate prevents the domain layer from depending on FastAPI or Pydantic API models.

The factory and repository work with domain `Device` objects. The API router converts them to `DeviceDto` objects using the mapper.

## Adding a Third Family

A third family could be added by creating another implementation of `DeviceFamilyFactory`.

For example, a `CloudDeviceFactory` could create the same types of devices but use cloud-based communication settings.

The new factory would then be added to `get_family_factory()`.

The existing repository and API could continue to work because they operate with the common `Device` model.