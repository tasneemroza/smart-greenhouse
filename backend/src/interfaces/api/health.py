from fastapi import APIRouter

from src.infrastructure.db import check_database_connection

router = APIRouter()


@router.get("/health")
def health_check():
    check_database_connection()
    return {"status": "ok", "db": "ok"}