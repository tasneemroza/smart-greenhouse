from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReadingDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    device_id: UUID
    value: float
    unit: str
    source: str
    recorded_at: datetime