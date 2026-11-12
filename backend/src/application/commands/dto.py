from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CommandRequest(BaseModel):
    command_type: str
    device_id: UUID
    payload: dict[str, Any] = Field(default_factory=dict)


class CommandResult(BaseModel):
    id: UUID
    command_type: str
    device_id: UUID
    payload: dict[str, Any]
    status: str
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
