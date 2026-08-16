from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.routers import data_health, drift, health, overview, predictions, scores, traffic
from app.services.drift_snapshot_job import start_scheduler

app = FastAPI(title="Credit Risk Ops Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(overview.router)
app.include_router(traffic.router)
app.include_router(scores.router)
app.include_router(drift.router)
app.include_router(predictions.router)
app.include_router(data_health.router)


@app.on_event("startup")
def on_startup():
    start_scheduler()
