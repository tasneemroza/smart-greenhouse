# State Pattern — Actuator Lifecycle

## 1. Purpose

The State pattern manages the lifecycle of each actuator.

An actuator can have different states, such as idle, running, error, or maintenance. Its available commands depend on its current state.

The purpose is to prevent invalid operations and keep actuator state consistent.

## 2. Architecture

The implementation follows the existing project architecture.

- **Domain:** `domain/actuators/state.py` defines the actuator states, allowed transitions, and available commands.
- **Application:** `application/devices/actuator_state_service.py` loads the current state, validates transitions, and saves valid changes.
- **DTO:** `application/devices/actuator_state_dto.py` defines the state response.
- **Infrastructure:** `infrastructure/persistence/models.py` defines the database model. `actuator_state_repository.py` handles database access.
- **API:** `interfaces/api/devices.py` exposes actuator state and the transition endpoint.
- **Frontend:** `DeviceList.tsx` displays the actuator state as a badge and shows allowed commands in its tooltip.

The domain layer owns the transition rules. The API does not implement the state machine.

## 3. Actuator states

| State | Meaning |
|---|---|
| off | The actuator is switched off. |
| idle | The actuator is available but not running. |
| running | The actuator is operating. |
| maintenance | The actuator is under maintenance. |
| error | The actuator has an error and needs a reset. |

## 4. Allowed transitions

| Current state | Allowed next states |
|---|---|
| off | idle, error |
| idle | running, off, maintenance, error |
| running | idle, maintenance, error |
| maintenance | idle, off, error |
| error | idle |

A transition not listed in this table is rejected.

Examples:
- idle -> running is allowed.
- running -> idle is allowed.
- running -> off is not allowed.
- error -> idle is allowed after reset.

An invalid transition raises `InvalidActuatorTransition`. The application service rolls back the database transaction and does not save the invalid state.

## 5. Allowed commands

| State | Pump command | Grow light command |
|---|---|---|
| off | power_on_pump | power_on_grow_light |
| idle | start_pump | start_grow_light |
| running | stop_pump | stop_grow_light |
| maintenance | resume_pump | resume_grow_light |
| error | reset_pump | reset_grow_light |

The domain context calculates the allowed command for the current state. Pump device types, including `water_pump` and `test_pump`, use the `pump` command name.

These commands describe the operations available to later phases. This phase does not execute physical actuator commands.

## 6. Database persistence

Actuator state is stored in the `actuator_states` table.

| Column | Description |
|---|---|
| device_id | UUID primary key and foreign key to `devices.id` |
| state | Current actuator state |
| updated_at | Timestamp of the latest state update |

The foreign key uses `ON DELETE CASCADE`.

The Alembic migration `f2550ae30b44_add_actuator_states.py` creates the table and initializes existing actuator devices with the `idle` state.

New actuators are initialized to `idle` when saved through the device repository.

Only actuators have lifecycle state records. Sensors return `state: null` and an empty `allowed_commands` list.

## 7. API

### Read devices

`GET /api/devices`

Device responses include:
- `state`
- `allowed_commands`

For actuators, these values reflect the persisted state. Sensor devices do not have an actuator state.

### Change actuator state

`POST /api/devices/{device_id}/transition`

Example request:

```json
{
  "target": "running"
}
```

Error responses:
- `404 Not Found`: the actuator does not exist.
- `409 Conflict`: the requested transition is not allowed or the actuator state has not been initialized.

The service locks the state row while applying a transition, validates the requested change, and saves only valid transitions.

## 8. Frontend

Actuator cards display a state badge.

The badge styles are:
- off and idle: slate
- running: emerald
- error: red
- maintenance: amber

The badge tooltip displays the allowed commands.

Sensor cards do not display actuator state badges.

## 9. Testing

The Phase 8 tests are in `backend/tests/test_phase8_state.py`.

They cover:
- Legal state transitions.
- Illegal transitions and unchanged state after rejection.
- Unknown state values.
- Allowed command mapping for pumps and grow lights.
- Successful persistence through the application service.
- Rollback and no save when a transition is invalid.

The live API was also checked:
- idle -> running returned `running` and `stop_pump`.
- running -> off returned HTTP 409 and kept the state as `running`.
- running -> idle returned `idle` and `start_pump`.

## 10. Relationship with later phases

Phase 9 can use the Decorator pattern to wrap actuator ports and log command attempts.

Phase 10 can use the Command pattern to execute operations while checking the actuator's current state and allowed commands.

The State pattern is responsible for lifecycle rules. It does not add a message broker, MQTT client, or physical device execution.