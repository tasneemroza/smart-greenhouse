from uuid import UUID

from src.application.automation.dto import (
    AutomationEvaluationDto,
    AutomationStrategyDto,
    ZoneRecommendationDto,
)
from src.domain.automation.entity import LocationAutomationContext
from src.domain.automation.strategies import get_strategy
from src.infrastructure.persistence.automation_repository import (
    AutomationRepository,
)


class AutomationService:
    def __init__(self, db) -> None:
        self.repository = AutomationRepository(db)

    def set_strategy(
        self,
        location_id: UUID,
        strategy_key: str,
    ) -> AutomationStrategyDto:
        get_strategy(strategy_key)

        location = self.repository.get_location(location_id)
        if location is None:
            raise LookupError("Location not found.")

        rule = self.repository.save_strategy(location_id, strategy_key)

        return AutomationStrategyDto(
            location_id=rule.location_id,
            strategy_key=rule.strategy_key,
            updated_at=rule.updated_at,
        )

    def evaluate(self, location_id: UUID) -> AutomationEvaluationDto:
        location = self.repository.get_location(location_id)
        if location is None:
            raise LookupError("Location not found.")

        rule = self.repository.get_rule(location_id)
        if rule is None:
            raise ValueError(
                "No automation strategy configured for this location."
            )

        strategy = get_strategy(rule.strategy_key)
        zones = self.repository.list_zones(location_id)
        recommendations = []

        for zone in zones:
            if not self.repository.has_moisture_sensor(zone.id):
                recommendations.append(
                    ZoneRecommendationDto(
                        zone_id=zone.id,
                        zone_name=zone.name,
                        action="wait",
                        reason="No moisture sensor in this zone.",
                    )
                )
                continue

            context = LocationAutomationContext(
                location_id=location_id,
                zone_id=zone.id,
                latest_moisture=self.repository.latest_value(
                    zone.id, "moisture_sensor"
                ),
                latest_light=self.repository.latest_value(
                    zone.id, "light_sensor"
                ),
                moisture_threshold_low=float(
                    zone.moisture_threshold_low
                ),
                moisture_threshold_high=float(
                    zone.moisture_threshold_high
                ),
            )

            recommendation = strategy.decide(context)

            recommendations.append(
                ZoneRecommendationDto(
                    zone_id=zone.id,
                    zone_name=zone.name,
                    action=recommendation.action,
                    reason=recommendation.reason,
                    score=recommendation.score,
                    intensity=recommendation.intensity,
                )
            )

        return AutomationEvaluationDto(
            location_id=location_id,
            strategy_key=rule.strategy_key,
            recommendations=recommendations,
        )
