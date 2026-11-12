from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.application.commands.dto import CommandRequest
from src.application.actuators.port_factory import build_actuator_port
from src.domain.actuators.state import ActuatorContext
from src.domain.commands.invoker import CommandInvoker, command_for
from src.infrastructure.db import SessionLocal
from src.infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)
from src.infrastructure.persistence.command_log_repository import (
    CommandLogRepository,
)


class CommandDeviceNotFoundError(LookupError):
    pass


class CommandStateNotFoundError(LookupError):
    pass


class CommandService:
    def __init__(self, db: Session):
        self.db = db
        self.state_repository = ActuatorStateRepository(db)
        self.log_repository = CommandLogRepository(db)
        self.invoker = CommandInvoker()

    def execute(self, request: CommandRequest):
        command = command_for(
            request.command_type,
            request.device_id,
            request.payload,
        )

        device = self.state_repository.get_actuator(request.device_id)

        if device is None:
            raise CommandDeviceNotFoundError("Actuator not found.")

        state_row = self.state_repository.get_state_for_update(
            request.device_id
        )

        if state_row is None:
            self.db.rollback()
            raise CommandStateNotFoundError(
                "Actuator state has not been initialized."
            )

        context = ActuatorContext(
            state=state_row.state,
            device_type=device.device_type,
        )

        if request.command_type not in context.allowed_commands():
            return self.log_repository.create(
                command_type=request.command_type,
                device_id=request.device_id,
                payload=request.payload,
                status="rejected",
                error_message=(
                    f"Command '{request.command_type}' is not allowed "
                    f"while actuator is '{context.state}'."
                ),
            )

        # Phase 9 logging uses a separate database session.
        # Its commits cannot release the Phase 10 state lock.
        try:
            with SessionLocal() as execution_db:
                port = build_actuator_port(execution_db)
                self.invoker.run(command, port)

        except Exception as error:
            self.db.rollback()

            return self.log_repository.create(
                command_type=request.command_type,
                device_id=request.device_id,
                payload=request.payload,
                status="failed",
                error_message=str(error),
            )

        if (
            command.target_state is not None
            and command.target_state != context.state
        ):
            context.transition(command.target_state)
            state_row.state = context.state
            state_row.updated_at = datetime.now(timezone.utc)
            self.db.add(state_row)

        return self.log_repository.create(
            command_type=request.command_type,
            device_id=request.device_id,
            payload=request.payload,
            status="success",
        )

    def list_recent(self, limit: int = 50):
        return self.log_repository.list_recent(limit)
