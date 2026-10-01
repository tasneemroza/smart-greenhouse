import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from src.application.sensors.reading_ingest import ReadingIngest
from src.application.sensors.simulation_sampler import SimulationSampler
from src.infrastructure.db import SessionLocal
from src.infrastructure.persistence.reading_repository import ReadingRepository
from src.infrastructure.settings import settings
from src.interfaces.api.devices import router as devices_router
from src.interfaces.api.health import router as health_router
from src.interfaces.api.locations import router as locations_router
from src.interfaces.api.sensors import router as sensors_router


async def run_simulation_sampler():
    while True:
        db = SessionLocal()

        try:
            repository = ReadingRepository(db)
            ingest = ReadingIngest(db, repository)
            sampler = SimulationSampler(db, ingest)
            sampler.run_once()
        except Exception:
            db.rollback()
        finally:
            db.close()

        await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    sampler_task = asyncio.create_task(
        run_simulation_sampler()
    )

    try:
        yield
    finally:
        sampler_task.cancel()

        try:
            await sampler_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Smart Greenhouse API",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.cors_origins.split(",")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Smart Greenhouse API"}


app.include_router(health_router)
app.include_router(sensors_router)
app.include_router(devices_router)
app.include_router(locations_router)


@app.get("/scalar", include_in_schema=False)
def scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Smart Greenhouse API",
    )