# Builder Pattern - Location Configuration

## Problem

A greenhouse location can contain different zones. Each zone needs a name, moisture thresholds, and a watering schedule.

Creating the configuration directly could allow invalid values to reach the database. The Builder Pattern keeps the configuration creation step-by-step and validates it before persistence.

## Builder Implementation

`LocationConfigBuilder` is responsible for creating a valid `LocationConfig`.

The builder provides fluent methods:

- `with_location_name()` sets the location name.
- `add_zone()` adds a zone.
- `build()` validates the configuration and creates the final `LocationConfig`.

The builder checks that:

- the location has a name
- at least one zone exists
- zone names are not empty
- moisture thresholds are between 0 and 1
- the low threshold is lower than the high threshold

Invalid configurations raise `ConfigurationError` before database persistence.

The builder does not attach devices. Device-to-zone assignment is handled separately after the zone has an ID.

## Why Builder?

Builder is useful here because the location configuration contains multiple parts and validation rules. The configuration can be created step-by-step instead of using one large constructor.

## Builder vs Factory Method

Factory Method is mainly used to create an object through a creation method, often allowing subclasses to decide which object is created.

Builder is different because it constructs one complex `LocationConfig` step-by-step and validates the complete result before it is created.

## Builder vs Abstract Factory

Abstract Factory creates families of related objects, such as simulation or edge devices in the previous phase.

Builder creates one complex `LocationConfig` from several configurable parts, such as the location and its zones.

## Persistence

After the Builder creates a valid configuration, the application service passes it to `LocationRepository`.

The repository saves the location first and then saves its zones using the generated `location_id`.

Each zone stores `location_id` as a foreign key to its location.

Device assignment is handled separately by the zone assignment service. Assigning a device to a zone copies the zone's `location_id` to the device, while unassigning clears both `zone_id` and `location_id`.

## API

The location configuration API provides:

- `POST /api/locations/config` - creates and persists a location configuration.
- `GET /api/locations/{location_id}/config` - retrieves a saved configuration.
- `GET /api/locations` - lists saved locations.
- `DELETE /api/locations/{location_id}` - deletes a saved location.
- `POST /api/locations/{location_id}/zones` - adds a zone.
- `PATCH /api/locations/{location_id}/zones/{zone_id}` - updates a zone.
- `DELETE /api/locations/{location_id}/zones/{zone_id}` - deletes a zone.

The API uses DTOs for request and response data.

## Extension Idea

The Builder could later support more configuration options, such as temperature limits, lighting schedules, or additional automation settings, without making the API or domain construction logic difficult to manage.
