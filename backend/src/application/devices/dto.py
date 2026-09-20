from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DeviceDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None
    device_type: str
    role: str
    device_family: str
    display_name: str
    default_config: dict