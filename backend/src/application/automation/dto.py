from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AutomationStrategyDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    location_id: UUID
    strategy_key: str
    updated_at: datetime


class ZoneRecommendationDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    zone_id: UUID
    zone_name: str
    action: str
    reason: str
    score: float | None = None
    intensity: float | None = None


class AutomationEvaluationDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    location_id: UUID
    strategy_key: str
    recommendations: list[ZoneRecommendationDto]
