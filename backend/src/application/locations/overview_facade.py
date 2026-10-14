from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.application.automation.service import AutomationService
from src.application.locations.overview_dto import (
    LocationOverviewDto,
    OverviewDeviceCountsDto,
    OverviewDeviceDto,
    OverviewLocationDto,
    OverviewReadingDto,
    OverviewRecommendationDto,
    OverviewZoneDto,
)
from src.infrastructure.persistence.automation_repository import (
    AutomationRepository,
)
from src.infrastructure.persistence.models import (
    DeviceRow,
    LocationRow,
    ReadingRow,
    ZoneRow,
)


class LocationOverviewFacade:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.automation_repository = AutomationRepository(db)
        self.automation_service = AutomationService(db)

    def get_overview(self, location_id: UUID) -> LocationOverviewDto:
        location = self.db.get(LocationRow, location_id)
        if location is None:
            raise LookupError("Location not found.")

        zones = list(
            self.db.scalars(
                select(ZoneRow)
                .where(ZoneRow.location_id == location_id)
                .order_by(ZoneRow.name)
            ).all()
        )

        zone_ids = [zone.id for zone in zones]
        devices = []

        if zone_ids:
            devices = list(
                self.db.scalars(
                    select(DeviceRow)
                    .where(DeviceRow.zone_id.in_(zone_ids))
                    .order_by(DeviceRow.display_name, DeviceRow.device_type)
                ).all()
            )

        devices_by_zone: dict[UUID, list[OverviewDeviceDto]] = {
            zone.id: [] for zone in zones
        }
        readings_by_zone: dict[UUID, list[OverviewReadingDto]] = {
            zone.id: [] for zone in zones
        }

        for device in devices:
            if device.zone_id is not None:
                devices_by_zone[device.zone_id].append(
                    OverviewDeviceDto(
                        id=device.id,
                        device_type=device.device_type,
                        role=device.role,
                        display_name=device.display_name or device.device_type,
                    )
                )

        device_ids = [device.id for device in devices]

        if device_ids:
            ranked_readings = (
                select(
                    ReadingRow.device_id.label("device_id"),
                    ReadingRow.value.label("value"),
                    ReadingRow.unit.label("unit"),
                    ReadingRow.recorded_at.label("recorded_at"),
                    func.row_number()
                    .over(
                        partition_by=ReadingRow.device_id,
                        order_by=(
                            ReadingRow.recorded_at.desc(),
                            ReadingRow.id.desc(),
                        ),
                    )
                    .label("row_number"),
                )
                .where(ReadingRow.device_id.in_(device_ids))
                .subquery()
            )

            latest_rows = self.db.execute(
                select(
                    ranked_readings.c.device_id,
                    ranked_readings.c.value,
                    ranked_readings.c.unit,
                    ranked_readings.c.recorded_at,
                ).where(ranked_readings.c.row_number == 1)
            ).all()

            devices_by_id = {device.id: device for device in devices}

            for reading in latest_rows:
                device = devices_by_id[reading.device_id]

                if device.zone_id is not None:
                    readings_by_zone[device.zone_id].append(
                        OverviewReadingDto(
                            device_id=reading.device_id,
                            value=float(reading.value),
                            unit=reading.unit,
                            recorded_at=reading.recorded_at,
                            tracking_enabled=device.tracking_enabled,
                            sampling_interval_seconds=(
                                device.sampling_interval_seconds
                            ),
                        )
                    )

        sensor_count = sum(
            1 for device in devices if device.role == "sensor"
        )
        actuator_count = sum(
            1 for device in devices if device.role == "actuator"
        )

        rule = self.automation_repository.get_rule(location_id)
        strategy_key = rule.strategy_key if rule is not None else None
        last_recommendation = None

        if strategy_key is not None:
            evaluation = self.automation_service.evaluate(location_id)

            if evaluation.recommendations:
                recommendation = evaluation.recommendations[0]
                last_recommendation = OverviewRecommendationDto(
                    action=recommendation.action,
                    reason=recommendation.reason,
                )

        overview_zones = [
            OverviewZoneDto(
                id=zone.id,
                name=zone.name,
                moisture_threshold_low=float(
                    zone.moisture_threshold_low
                ),
                moisture_threshold_high=float(
                    zone.moisture_threshold_high
                ),
                devices=devices_by_zone[zone.id],
                latest_readings=readings_by_zone[zone.id],
            )
            for zone in zones
        ]

        return LocationOverviewDto(
            location=OverviewLocationDto(
                id=location.id,
                name=location.name,
            ),
            device_counts=OverviewDeviceCountsDto(
                sensor=sensor_count,
                actuator=actuator_count,
            ),
            zones=overview_zones,
            strategy_key=strategy_key,
            last_recommendation=last_recommendation,
        )
