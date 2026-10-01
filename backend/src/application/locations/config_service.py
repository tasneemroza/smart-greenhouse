from uuid import UUID

from src.domain.locations.config_builder import LocationConfigBuilder

from .dto import (
    BuildLocationConfigRequestDto,
    LocationConfigDto,
    ZoneConfigDto,
)
from .mappers import location_config_to_dto


class LocationConfigService:
    def __init__(self, repository) -> None:
        self._repository = repository

    def build_and_save(
        self,
        request: BuildLocationConfigRequestDto,
    ) -> LocationConfigDto:
        builder = LocationConfigBuilder().with_location_name(
            request.location_name
        )

        for zone in request.zones:
            builder.add_zone(
                name=zone.name,
                moisture_threshold_low=zone.moisture_threshold_low,
                moisture_threshold_high=zone.moisture_threshold_high,
                schedule=zone.schedule,
            )

        config = builder.build()

        location_row, zone_rows = self._repository.save_config(config)

        return location_config_to_dto(
            location_row,
            zone_rows,
        )

    def get_config(
        self,
        location_id: UUID,
    ) -> LocationConfigDto | None:
        result = self._repository.get_config(location_id)

        if result is None:
            return None

        location_row, zone_rows = result

        return location_config_to_dto(
            location_row,
            zone_rows,
        )

    def list_locations(self):
        return self._repository.list_locations()

    def delete_location(
        self,
        location_id: UUID,
    ) -> bool:
        return self._repository.delete_location(location_id)

    def add_zone(
        self,
        location_id: UUID,
        name: str,
        moisture_threshold_low: float,
        moisture_threshold_high: float,
        schedule: dict,
    ):
        self._validate_zone(
            name,
            moisture_threshold_low,
            moisture_threshold_high,
            schedule,
        )

        return self._repository.add_zone(
            location_id=location_id,
            name=name,
            moisture_threshold_low=moisture_threshold_low,
            moisture_threshold_high=moisture_threshold_high,
            schedule=schedule,
        )

    def update_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
        name: str,
        moisture_threshold_low: float,
        moisture_threshold_high: float,
        schedule: dict,
    ):
        self._validate_zone(
            name,
            moisture_threshold_low,
            moisture_threshold_high,
            schedule,
        )

        return self._repository.update_zone(
            location_id=location_id,
            zone_id=zone_id,
            name=name,
            moisture_threshold_low=moisture_threshold_low,
            moisture_threshold_high=moisture_threshold_high,
            schedule=schedule,
        )

    def delete_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> str:
        return self._repository.delete_zone(
            location_id,
            zone_id,
        )

    def list_zones(
        self,
        location_id: UUID,
    ):
        return self._repository.list_zones(location_id)

    @staticmethod
    def _validate_zone(
        name: str,
        moisture_threshold_low: float,
        moisture_threshold_high: float,
        schedule: dict,
    ) -> None:
        if not name.strip():
            raise ValueError("Zone name is required.")

        if (
            moisture_threshold_low < 0
            or moisture_threshold_low > 1
            or moisture_threshold_high < 0
            or moisture_threshold_high > 1
        ):
            raise ValueError(
                "Moisture thresholds must be between 0 and 1."
            )

        if moisture_threshold_low >= moisture_threshold_high:
            raise ValueError(
                "Low moisture threshold must be lower than high threshold."
            )

        if not schedule:
            raise ValueError("Schedule is required.")