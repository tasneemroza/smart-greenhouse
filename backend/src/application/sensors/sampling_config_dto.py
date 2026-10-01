from pydantic import BaseModel, Field


class SamplingConfigDto(BaseModel):
    sampling_interval_seconds: int = Field(
        ge=5,
    )
    tracking_enabled: bool