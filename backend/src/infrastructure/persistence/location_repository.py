from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from src.domain.locations.entity import LocationConfig

from .models import DeviceRow, LocationRow, ZoneRow


class LocationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save_config(
        self,
        config: LocationConfig,
    ) -> tuple[LocationRow, list[ZoneRow]]:
        try:
            location = LocationRow(
                name=config.location.name,
            )

            self._session.add(location)
            self._session.flush()

            zones: list[ZoneRow] = []

            for zone in config.location.zones:
                zone_row = ZoneRow(
                    location_id=location.id,
                    name=zone.name,
                    moisture_threshold_low=zone.moisture_threshold_low,
                    moisture_threshold_high=zone.moisture_threshold_high,
                    schedule=zone.schedule,
                )

                self._session.add(zone_row)
                zones.append(zone_row)

            self._session.commit()

            self._session.refresh(location)

            for zone in zones:
                self._session.refresh(zone)

            return location, zones

        except Exception:
            self._session.rollback()
            raise

    def get_config(
        self,
        location_id: UUID,
    ) -> tuple[LocationRow, list[ZoneRow]] | None:
        location = self._session.get(LocationRow, location_id)

        if location is None:
            return None

        zones = list(
            self._session.scalars(
                select(ZoneRow)
                .where(ZoneRow.location_id == location_id)
                .order_by(ZoneRow.name)
            )
        )

        return location, zones

    def list_locations(self) -> list[LocationRow]:
        return list(
            self._session.scalars(
                select(LocationRow).order_by(LocationRow.name)
            )
        )

    def delete_location(self, location_id: UUID) -> bool:
        location = self._session.get(LocationRow, location_id)

        if location is None:
            return False

        try:
            self._session.execute(
                update(DeviceRow)
                .where(DeviceRow.location_id == location_id)
                .values(
                    location_id=None,
                    zone_id=None,
                )
            )

            self._session.delete(location)
            self._session.commit()

            return True

        except Exception:
            self._session.rollback()
            raise

    def get_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> ZoneRow | None:
        return self._session.scalar(
            select(ZoneRow).where(
                ZoneRow.id == zone_id,
                ZoneRow.location_id == location_id,
            )
        )

    def list_zones(
        self,
        location_id: UUID,
    ) -> list[ZoneRow] | None:
        location = self._session.get(LocationRow, location_id)

        if location is None:
            return None

        return list(
            self._session.scalars(
                select(ZoneRow)
                .where(ZoneRow.location_id == location_id)
                .order_by(ZoneRow.name)
            )
        )

    def add_zone(
        self,
        location_id: UUID,
        name: str,
        moisture_threshold_low: float,
        moisture_threshold_high: float,
        schedule: dict,
    ) -> ZoneRow | None:
        location = self._session.get(LocationRow, location_id)

        if location is None:
            return None

        try:
            zone = ZoneRow(
                location_id=location_id,
                name=name,
                moisture_threshold_low=moisture_threshold_low,
                moisture_threshold_high=moisture_threshold_high,
                schedule=schedule,
            )

            self._session.add(zone)
            self._session.commit()
            self._session.refresh(zone)

            return zone

        except Exception:
            self._session.rollback()
            raise

    def update_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
        name: str,
        moisture_threshold_low: float,
        moisture_threshold_high: float,
        schedule: dict,
    ) -> ZoneRow | None:
        zone = self.get_zone(location_id, zone_id)

        if zone is None:
            return None

        try:
            zone.name = name
            zone.moisture_threshold_low = moisture_threshold_low
            zone.moisture_threshold_high = moisture_threshold_high
            zone.schedule = schedule

            self._session.commit()
            self._session.refresh(zone)

            return zone

        except Exception:
            self._session.rollback()
            raise

    def delete_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> str:
        zone = self.get_zone(location_id, zone_id)

        if zone is None:
            return "missing"

        zone_count = self._session.scalar(
            select(ZoneRow.id)
            .where(ZoneRow.location_id == location_id)
            .limit(2)
        )

        all_zones = list(
            self._session.scalars(
                select(ZoneRow.id)
                .where(ZoneRow.location_id == location_id)
            )
        )

        if len(all_zones) <= 1:
            return "last"

        try:
            self._session.execute(
                update(DeviceRow)
                .where(DeviceRow.zone_id == zone_id)
                .values(
                    zone_id=None,
                    location_id=None,
                )
            )

            self._session.delete(zone)
            self._session.commit()

            return "deleted"

        except Exception:
            self._session.rollback()
            raise

    def list_zone_devices(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> list[DeviceRow] | None:
        zone = self.get_zone(location_id, zone_id)

        if zone is None:
            return None

        return list(
            self._session.scalars(
                select(DeviceRow)
                .where(DeviceRow.zone_id == zone_id)
                .order_by(DeviceRow.display_name, DeviceRow.id)
            )
        )

    def assign_device_to_zone(
        self,
        device_id: UUID,
        zone_id: UUID | None,
    ) -> DeviceRow | None:
        device = self._session.get(DeviceRow, device_id)

        if device is None:
            return None

        try:
            if zone_id is None:
                device.zone_id = None
                device.location_id = None
            else:
                zone = self._session.get(ZoneRow, zone_id)

                if zone is None:
                    raise ValueError("Zone not found.")

                device.zone_id = zone.id
                device.location_id = zone.location_id

            self._session.commit()
            self._session.refresh(device)

            return device

        except Exception:
            self._session.rollback()
            raise