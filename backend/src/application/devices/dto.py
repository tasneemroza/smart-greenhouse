from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DeviceDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None
    device_type: str
    role: str
    device_family: str
    display_name: str
    default_config: dict
    location_id: UUID | None
    zone_id: UUID | None
    state: str | None = None
    allowed_commands: list[str] = Field(default_factory=list)
