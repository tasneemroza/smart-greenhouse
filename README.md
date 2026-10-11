# Smart Greenhouse

Smart Greenhouse is a course project for practising software design patterns while developing a greenhouse monitoring application.

The application uses FastAPI, PostgreSQL, React, TypeScript, and Vite.

## Features and design patterns

- Factory Method: creates individual device types.
- Abstract Factory: creates related families of devices.
- Builder: constructs and validates location configurations.
- Adapter: converts sensor data from different sources into a common reading format.
- Strategy: selects an automation recommendation algorithm.

Automation strategies provide recommendations; they do not directly control physical actuators.

## Prerequisites

- Git
- Docker Desktop with Docker Compose

## Setup

Open PowerShell and navigate to the project:

```powershell
cd "D:\DESIGN PATTERN-26\smart-greenhouse"
```

If `.env` does not exist, create it from the example:

```powershell
if (!(Test-Path .env)) {
    Copy-Item .env.example .env
}
```

Start the application:

```powershell
docker compose up --build -d
```

Check the services:

```powershell
docker compose ps
```

## Application URLs

- Frontend: http://localhost:5173
- Backend health: http://localhost:8000/health
- API documentation: http://localhost:8000/scalar

## Tests

Run all backend tests:

```powershell
docker compose exec backend pytest tests -q
```

Run Phase 5 Adapter tests:

```powershell
docker compose exec backend pytest tests/test_phase5_adapter.py -q
```

Run Phase 6 Strategy tests:

```powershell
docker compose exec backend pytest tests/test_phase6_strategy.py -q
docker compose exec backend pytest tests/test_phase6_strategy_api.py -q
```

## Stop the application

```powershell
docker compose down
```

This normally retains the PostgreSQL data volume. Do not add `-v` unless you intentionally want to remove Compose-managed volumes.

## Documentation

Design-pattern guides are located in `docs/patterns/`:

- `factory-method.md`
- `abstract-factory.md`
- `builder.md`
- `adapter.md`
- `strategy.md`

## Project structure

```text
smart-greenhouse/
├── backend/
│   ├── src/
│   └── tests/
├── docs/
│   └── patterns/
├── frontend/
├── docker-compose.yml
├── .env.example
└── README.md
```