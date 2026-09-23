from src.domain.locations.entity import LocationConfig

from .dto import LocationConfigDto, LocationDto, ZoneConfigDto


def location_config_to_dto(
    location_row,
    zone_rows,
) -> LocationConfigDto:
    return LocationConfigDto(
        location=LocationDto(
            id=location_row.id,
            name=location_row.name,
        ),
        zones=[
            ZoneConfigDto(
                id=zone.id,
                location_id=zone.location_id,
                name=zone.name,
                moisture_threshold_low=float(zone.moisture_threshold_low),
                moisture_threshold_high=float(zone.moisture_threshold_high),
                schedule=zone.schedule,
            )
            for zone in zone_rows
        ],
    )


def request_to_builder_data(request) -> LocationConfig:
    from src.domain.locations.config_builder import LocationConfigBuilder

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

    return builder.build()