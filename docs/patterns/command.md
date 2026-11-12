# Phase 10 - Command Pattern

## Purpose
The Command pattern encapsulates actuator operations as command objects. It separates command creation from execution and supports audit logging.

## Implementation
The commands are implemented in backend/src/domain/commands/.

Commands:
- StartPumpCommand
- StopPumpCommand
- StartGrowLightCommand
- StopGrowLightCommand
- SetLightLevelCommand

CommandInvoker executes commands through ActuatorPort.
The command registry maps command names to their classes.

## Integration
Phase 8 State pattern checks allowed commands before execution.
Phase 9 Decorator pattern applies runtime policies and execution logging.

## API
POST /api/commands executes a command.
GET /api/commands retrieves command history.

Possible statuses:
- success
- rejected
- failed

## Database
The command_log table stores the command ID, device ID, command type, payload, status, error message, and timestamp.

## Frontend
The Controls page allows users to:
- Select actuators
- Start and stop pumps
- Start and stop grow lights
- Adjust grow-light brightness
- View recent command history

## Testing
Phase 10 unit tests: 16 passed.
Complete backend test suite: 85 passed.
Frontend TypeScript and production build: passed.

Manual tests verified successful, rejected, and failed commands.

## Conclusion
The Command pattern provides structured actuator control and persistent audit history while integrating with the State and Decorator patterns.
