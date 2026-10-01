from pydantic import BaseModel


class SamplingConfigDto(BaseModel):
    sampling_interval_seconds: int
    tracking_enabled: bool