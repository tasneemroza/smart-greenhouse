from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.application.actuators.actuator_execution_service import (
    ActuatorExecutionService,
)
from src.application.devices.actuator_state_service import (
    ActuatorNotFoundError,
    ActuatorStateNotFoundError,
)
from src.infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRunTimeExceededError,
)
from src.infrastructure.db import get_db


router = APIRouter(prefix="/api/actuators", tags=["actuators"])


class ExecutionDto(BaseModel):
    id: UUID
    device_id: UUID
    success: bool
    policy_applied: list[str]
    message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ApplyRequest(BaseModel):
    command: str
    payload: dict = Field(default_factory=dict)


def get_execution_service(
    db: Session = Depends(get_db),
) -> ActuatorExecutionService:
    return ActuatorExecutionService(db)


@router.get("/executions", response_model=list[ExecutionDto])
def list_executions(
    limit: int = Query(default=20, ge=1, le=100),
    service: ActuatorExecutionService = Depends(get_execution_service),
):
    return service.list_recent(limit)


@router.post("/{device_id}/apply")
def apply_actuator(
    device_id: UUID,
    request: ApplyRequest,
    service: ActuatorExecutionService = Depends(get_execution_service),
):
    try:
        service.apply(
            device_id=device_id,
            command=request.command,
            payload=request.payload,
        )
    except ActuatorNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except ActuatorStateNotFoundError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error
    except MaxRunTimeExceededError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    return {
        "device_id": device_id,
        "success": True,
        "message": None,
        "policy_applied": ["logging"],
    }
