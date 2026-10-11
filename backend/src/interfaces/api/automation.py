from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.application.automation.dto import (
    AutomationEvaluationDto,
    AutomationStrategyDto,
)
from src.application.automation.service import AutomationService
from src.infrastructure.db import get_db


router = APIRouter(tags=["automation"])


class SetAutomationStrategyRequest(BaseModel):
    strategy_key: str


@router.put(
    "/api/locations/{location_id}/automation",
    response_model=AutomationStrategyDto,
)
def set_automation_strategy(
    location_id: UUID,
    payload: SetAutomationStrategyRequest,
    db: Session = Depends(get_db),
) -> AutomationStrategyDto:
    service = AutomationService(db)

    try:
        return service.set_strategy(
            location_id=location_id,
            strategy_key=payload.strategy_key,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


@router.post(
    "/api/locations/{location_id}/automation/evaluate",
    response_model=AutomationEvaluationDto,
)
def evaluate_automation(
    location_id: UUID,
    db: Session = Depends(get_db),
) -> AutomationEvaluationDto:
    service = AutomationService(db)

    try:
        return service.evaluate(location_id)
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
