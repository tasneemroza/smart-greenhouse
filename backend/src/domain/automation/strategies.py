from abc import ABC, abstractmethod

from src.domain.automation.entity import (
    LocationAutomationContext,
    Recommendation,
)


class AutomationStrategy(ABC):
    @abstractmethod
    def decide(
        self,
        context: LocationAutomationContext,
    ) -> Recommendation:
        raise NotImplementedError


class ConservativeMoistureStrategy(AutomationStrategy):
    def decide(
        self,
        context: LocationAutomationContext,
    ) -> Recommendation:
        moisture = context.latest_moisture

        if moisture is None:
            return Recommendation(
                action="wait",
                reason="No moisture reading is available.",
            )

        if moisture < context.moisture_threshold_low:
            return Recommendation(
                action="water",
                reason="Moisture is below the configured lower threshold.",
                intensity=0.5,
            )

        return Recommendation(
            action="wait",
            reason="Moisture is within or above the configured safe band.",
        )


class AggressiveMoistureStrategy(AutomationStrategy):
    def decide(
        self,
        context: LocationAutomationContext,
    ) -> Recommendation:
        moisture = context.latest_moisture

        if moisture is None:
            return Recommendation(
                action="wait",
                reason="No moisture reading is available.",
            )

        if moisture < context.moisture_threshold_high:
            return Recommendation(
                action="water",
                reason="Aggressive mode waters before moisture reaches the upper threshold.",
                intensity=1.0,
            )

        return Recommendation(
            action="wait",
            reason="Moisture has reached or exceeded the upper threshold.",
        )


def get_strategy(key: str) -> AutomationStrategy:
    strategies = {
        "conservative": ConservativeMoistureStrategy,
        "aggressive": AggressiveMoistureStrategy,
    }

    strategy_class = strategies.get(key)

    if strategy_class is None:
        raise ValueError(f"Unknown automation strategy: {key}")

    return strategy_class()
