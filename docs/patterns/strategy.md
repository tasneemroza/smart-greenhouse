# Strategy Pattern — Smart Greenhouse

## Purpose

The Strategy Pattern lets the application choose between different automation algorithms without changing the service that runs them.

In this project, the strategies evaluate moisture readings and zone thresholds to produce recommendations. They do not directly control pumps or other actuators.

## Strategy interface

`AutomationStrategy` defines the `decide(context)` operation. Each concrete strategy receives a `LocationAutomationContext` and returns a `Recommendation`.

The context contains the location and zone identifiers, latest moisture and optional light readings, and the configured lower and upper moisture thresholds. It contains plain Python values rather than database ORM objects.

## Concrete strategies

- **ConservativeMoistureStrategy** recommends watering when moisture is below the configured lower threshold. Otherwise, it recommends waiting.
- **AggressiveMoistureStrategy** recommends watering when moisture is below the configured upper threshold. Otherwise, it recommends waiting.

Both strategies return a wait recommendation when no moisture reading is available. The service also returns a wait recommendation when a zone has no assigned moisture sensor.

## Strategy selection

`get_strategy(key)` creates the requested strategy using its registered key. Unknown keys raise a `ValueError` rather than silently choosing a default strategy.

`AutomationService.set_strategy()` validates the key and persists it for the location in `automation_rules`. `AutomationService.evaluate()` loads the saved strategy, reads the latest sensor readings for each zone, uses that zone's configured thresholds, and asks the strategy for a recommendation.

The API exposes strategy selection through `PUT /api/locations/{location_id}/automation` and evaluation through `POST /api/locations/{location_id}/automation/evaluate`.

## Why this pattern is useful

The service does not need separate conditional logic for every automation algorithm. A new strategy can implement the same interface and be registered in the strategy factory. The existing service can then use it without being rewritten.

## Tests

The Phase 6 unit tests verify that:

- The conservative strategy waits when moisture is within the configured band.
- The conservative and aggressive strategies produce different recommendations for the same context.
- Missing moisture data produces a wait recommendation.
- An unknown strategy key is rejected.
