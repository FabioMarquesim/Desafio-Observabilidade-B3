import asyncio
import logging
import random
import secrets

from fastapi import FastAPI, HTTPException, Query

from app.logging_config import setup_logging
from app.telemetry import setup_telemetry
from app.metrics import setup_metrics

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Stream Authorization Service")
setup_telemetry(app)
setup_metrics(app)

SERVER_REGION = "sa-east-1"
FAILURE_RATE = 0.10  # ~10% de falha na "API externa"


class ExternalServiceError(Exception):
    """Falha na chamada ao serviço externo simulado."""


async def call_entitlement_service(user_id: str, movie_id: str) -> float:
    latency = random.uniform(0.05, 0.5)
    await asyncio.sleep(latency)

    if random.random() < FAILURE_RATE:
        raise ExternalServiceError("entitlement service unavailable")

    return latency


def choose_resolution(latency: float) -> str:
    if latency < 0.15:
        return "4K"
    if latency < 0.30:
        return "1080p"
    return "720p"


@app.get("/stream/authorize")
async def authorize(
    user_id: str = Query(..., min_length=1),
    movie_id: str = Query(..., min_length=1),
):
    try:
        latency = await call_entitlement_service(user_id, movie_id)
    except ExternalServiceError:
        logger.error(
            "entitlement service failed",
            extra={"user_id": user_id, "movie_id": movie_id},
        )
        raise HTTPException(
            status_code=503,
            detail="Serviço de autorização temporariamente indisponível",
        )

    resolution = choose_resolution(latency)
    logger.info(
        "stream authorized",
        extra={
            "user_id": user_id,
            "movie_id": movie_id,
            "resolution": resolution,
            "latency_ms": round(latency * 1000),
        },
    )

    return {
        "user_id": user_id,
        "movie_id": movie_id,
        "authorized": True,
        "resolution": resolution,
        "drm_token": secrets.token_urlsafe(32),
        "server_region": SERVER_REGION,
    }