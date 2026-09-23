from .entity import Location, LocationConfig, Zone
from .errors import ConfigurationError


class LocationConfigBuilder:
    def __init__(self) -> None:
        self._location_name: str | None = None
        self._zones: list[Zone] = []

    def with_location_name(self, name: str) -> "LocationConfigBuilder":
        self._location_name = name.strip()
        return self

    def add_zone(
        self,
        name: str,
        moisture_threshold_low: float,
        moisture_threshold_high: float,
        schedule: dict | None = None,
    ) -> "LocationConfigBuilder":
        self._zones.append(
            Zone(
                name=name.strip(),
                moisture_threshold_low=float(moisture_threshold_low),
                moisture_threshold_high=float(moisture_threshold_high),
                schedule=dict(schedule or {}),
            )
        )
        return self

    def build(self) -> LocationConfig:
        if not self._location_name:
            raise ConfigurationError("Location name is required.")

        if not self._zones:
            raise ConfigurationError("At least one zone is required.")

        for zone in self._zones:
            if not zone.name:
                raise ConfigurationError("Zone name is required.")

            if not 0.0 <= zone.moisture_threshold_low <= 1.0:
                raise ConfigurationError(
                    "Low moisture threshold must be between 0 and 1."
                )

            if not 0.0 <= zone.moisture_threshold_high <= 1.0:
                raise ConfigurationError(
                    "High moisture threshold must be between 0 and 1."
                )

            if zone.moisture_threshold_low >= zone.moisture_threshold_high:
                raise ConfigurationError(
                    "Low moisture threshold must be lower than high threshold."
                )

        return LocationConfig(
            location=Location(
                name=self._location_name,
                zones=tuple(self._zones),
            )
        )