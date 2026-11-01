from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ActuatorStateDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    device_id: UUID
    state: str
    updated_at: datetime
    allowed_commands: list[str]
