# Decorator Pattern — Phase 9

## Purpose

The Decorator pattern allows us to add extra behaviour around an actuator without changing the actuator adapter itself.

In the Smart Greenhouse application, the decorators add execution logging and a maximum runtime policy.

## Decorator Chain

The actuator execution service builds the following chain:

LoggingActuatorDecorator
    -> MaxRunTimeActuatorDecorator
        -> SimulationActuatorAdapter

Each decorator implements the same ActuatorPort interface.

Callers use ActuatorPort.apply(device_id, command, payload) without needing to know which decorators are installed.

## Logging Decorator

LoggingActuatorDecorator records each execution attempt in the PostgreSQL actuator_execution_log table.

Successful executions are saved with:

- success = true
- policy_applied = ["logging"]
- message = null

If the maximum runtime policy blocks execution, the log contains:

- success = false
- policy_applied = ["maxRunTime", "logging"]
- message = "Max run time exceeded"

## Maximum Runtime Decorator

MaxRunTimeActuatorDecorator reads the persisted actuator state.

If the actuator is in the running state and its updated_at timestamp is at least 30 minutes old, the decorator raises MaxRunTimeExceededError.

The inner simulation adapter is not called when this happens.

For other states, or when the running time is below 30 minutes, the command is forwarded to the inner adapter.

## Database Persistence

Execution attempts are stored in actuator_execution_log.

Each row contains the execution ID, device ID, success flag, applied policies, optional message, and creation timestamp.

The execution log repository saves records using SQLAlchemy.

## API

GET /api/actuators/executions?limit=20

Returns recent execution records, newest first.

POST /api/actuators/{device_id}/apply

Applies a simulated actuator command through the decorator chain.

A command blocked by the maximum runtime policy returns HTTP 409.

## Frontend

The React dashboard includes an Actuator Execution Log table.

It displays timestamps, device IDs, execution status, applied policies, and error messages.

The Refresh button reloads recent records from the API.

## Phase 9 Scope

Command strings are forwarded without command validation. Command validation belongs to Phase 10.

No scheduler or MQTT execution mechanism was added.

## Verification

Automated tests cover successful execution, unknown commands, the 30-minute boundary, blocked inner-adapter calls, and logging of execution attempts.

The API was also tested manually with successful and blocked actuator commands, and both records were confirmed through the execution-log endpoint.
