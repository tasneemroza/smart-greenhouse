from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.persistence.models import CommandLogRow


class CommandLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        command_type: str,
        device_id: UUID,
        payload: dict,
        status: str,
        error_message: str | None = None,
    ) -> CommandLogRow:
        if status not in {"success", "failed", "rejected"}:
            raise ValueError(f"Invalid command status: {status}")

        row = CommandLogRow(
            command_type=command_type,
            device_id=device_id,
            payload=payload,
            status=status,
            error_message=error_message,
        )

        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def list_recent(self, limit: int = 50) -> list[CommandLogRow]:
        statement = (
            select(CommandLogRow)
            .order_by(
                CommandLogRow.created_at.desc(),
                CommandLogRow.id.desc(),
            )
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())
