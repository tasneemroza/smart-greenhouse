from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from src.interfaces.api.health import router as health_router


app = FastAPI(
    title="Smart Greenhouse API",
    docs_url=None,
    redoc_url=None,
)


@app.get("/")
def root():
    return {"message": "Smart Greenhouse API"}


app.include_router(health_router)


@app.get("/scalar", include_in_schema=False)
def scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Smart Greenhouse API",
    )