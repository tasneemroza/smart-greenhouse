from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.persistence.models import (
    AutomationRuleRow,
    DeviceRow,
    LocationRow,
    ReadingRow,
    ZoneRow,
)


class AutomationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_location(self, location_id: UUID) -> LocationRow | None:
        return self._session.get(LocationRow, location_id)

    def get_rule(self, location_id: UUID) -> AutomationRuleRow | None:
        return self._session.scalar(
            select(AutomationRuleRow).where(
                AutomationRuleRow.location_id == location_id
            )
        )

    def save_strategy(
        self,
        location_id: UUID,
        strategy_key: str,
    ) -> AutomationRuleRow:
        try:
            rule = self.get_rule(location_id)

            if rule is None:
                rule = AutomationRuleRow(
                    location_id=location_id,
                    strategy_key=strategy_key,
                    parameters=None,
                )
                self._session.add(rule)
            else:
                rule.strategy_key = strategy_key
                rule.updated_at = datetime.now(timezone.utc)

            self._session.commit()
            self._session.refresh(rule)
            return rule
        except Exception:
            self._session.rollback()
            raise

    def list_zones(self, location_id: UUID) -> list[ZoneRow]:
        return list(
            self._session.scalars(
                select(ZoneRow)
                .where(ZoneRow.location_id == location_id)
                .order_by(ZoneRow.name)
            )
        )

    def has_moisture_sensor(self, zone_id: UUID) -> bool:
        sensor_id = self._session.scalar(
            select(DeviceRow.id)
            .where(
                DeviceRow.zone_id == zone_id,
                DeviceRow.device_type == "moisture_sensor",
                DeviceRow.role == "sensor",
            )
            .limit(1)
        )
        return sensor_id is not None

    def latest_value(
        self,
        zone_id: UUID,
        device_type: str,
    ) -> float | None:
        value = self._session.scalar(
            select(ReadingRow.value)
            .join(DeviceRow, ReadingRow.device_id == DeviceRow.id)
            .where(
                DeviceRow.zone_id == zone_id,
                DeviceRow.device_type == device_type,
                DeviceRow.role == "sensor",
            )
            .order_by(ReadingRow.recorded_at.desc())
            .limit(1)
        )
        return float(value) if value is not None else None
