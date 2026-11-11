from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.persistence.models import ActuatorExecutionLogRow


class ExecutionLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        device_id: UUID,
        success: bool,
        policy_applied: list[str],
        message: str | None = None,
    ) -> ActuatorExecutionLogRow:
        row = ActuatorExecutionLogRow(
            device_id=device_id,
            success=success,
            policy_applied=policy_applied,
            message=message,
        )

        try:
            self.db.add(row)
            self.db.commit()
            self.db.refresh(row)
            return row
        except Exception:
            self.db.rollback()
            raise

    def list_recent(
        self,
        limit: int = 20,
    ) -> list[ActuatorExecutionLogRow]:
        statement = (
            select(ActuatorExecutionLogRow)
            .order_by(
                ActuatorExecutionLogRow.created_at.desc(),
                ActuatorExecutionLogRow.id.desc(),
            )
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())
