from datetime import datetime

from pydantic import BaseModel


class SamplingResultDto(BaseModel):
    checked: int
    sampled: int
    skipped: int
    recorded_at: datetime