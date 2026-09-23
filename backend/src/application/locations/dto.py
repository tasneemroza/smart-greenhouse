from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ZoneConfigRequestDto(BaseModel):
    name: str
    moisture_threshold_low: float
    moisture_threshold_high: float
    schedule: dict[str, Any] = Field(default_factory=dict)


class BuildLocationConfigRequestDto(BaseModel):
    location_name: str
    zones: list[ZoneConfigRequestDto]


class LocationDto(BaseModel):
    id: UUID
    name: str


class ZoneConfigDto(BaseModel):
    id: UUID
    location_id: UUID
    name: str
    moisture_threshold_low: float
    moisture_threshold_high: float
    schedule: dict[str, Any]


class LocationConfigDto(BaseModel):
    location: LocationDto
    zones: list[ZoneConfigDto]