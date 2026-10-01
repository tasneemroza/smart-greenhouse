from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.sensors.reading import Reading
from src.infrastructure.persistence.models import ReadingRow


class ReadingRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, reading: Reading) -> Reading:
        row = ReadingRow(
            device_id=reading.device_id,
            value=reading.value,
            unit=reading.unit,
            source=reading.source,
            recorded_at=reading.recorded_at,
        )

        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)

        return self._row_to_reading(row)

    def list_for_device(
        self,
        device_id: UUID,
        limit: int = 20,
    ) -> list[Reading]:
        statement = (
            select(ReadingRow)
            .where(ReadingRow.device_id == device_id)
            .order_by(ReadingRow.recorded_at.desc())
            .limit(limit)
        )

        rows = self.db.scalars(statement).all()

        return [self._row_to_reading(row) for row in rows]

    def latest_for_device(
        self,
        device_id: UUID,
    ) -> Reading | None:
        statement = (
            select(ReadingRow)
            .where(ReadingRow.device_id == device_id)
            .order_by(ReadingRow.recorded_at.desc())
            .limit(1)
        )

        row = self.db.scalars(statement).first()

        if row is None:
            return None

        return self._row_to_reading(row)

    @staticmethod
    def _row_to_reading(row: ReadingRow) -> Reading:
        return Reading(
            device_id=row.device_id,
            value=float(row.value),
            unit=row.unit,
            source=row.source,
            recorded_at=row.recorded_at,
        )