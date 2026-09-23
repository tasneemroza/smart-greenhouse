from src.domain.locations.config_builder import LocationConfigBuilder

from .dto import BuildLocationConfigRequestDto, LocationConfigDto
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

    def get_config(self, location_id):
        result = self._repository.get_config(location_id)

        if result is None:
            return None

        location_row, zone_rows = result

        return location_config_to_dto(
            location_row,
            zone_rows,
        )