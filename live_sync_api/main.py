import logging
import os

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from .telemetry import setup_telemetry

setup_telemetry()

logger = logging.getLogger("live_sync_api")

app = FastAPI(title="Mainstage Live Sync API")

FastAPIInstrumentor.instrument_app(app)

MUSIC_API_URL = os.environ.get("MUSIC_API_URL", "http://mock-music-api:9000")
COLLECTOR_METRICS_URL = os.environ.get("COLLECTOR_METRICS_URL", "http://otel-lgtm:8889/metrics")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics(request: Request):
    try:
        response = httpx.get(
            COLLECTOR_METRICS_URL,
            headers={"Accept": request.headers.get("accept", "")},
            timeout=5.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error(f"collector metrics endpoint unavailable error={exc}")
        raise HTTPException(status_code=503, detail="metrics backend unavailable")

    return Response(
        content=response.content,
        media_type=response.headers.get("content-type", "text/plain"),
    )


@app.get("/live-sync/track")
def live_sync_track(artist: str, title: str):
    logger.info(f"live_sync_track request received artist={artist} title={title}")
    try:
        response = httpx.get(
            f"{MUSIC_API_URL}/track-metadata",
            params={"artist": artist, "title": title},
            timeout=2.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error(f"external streaming API failed artist={artist} title={title} error={exc}")
        raise HTTPException(status_code=503, detail="external streaming API unavailable")

    metadata = response.json()
    sync_delay_ms = round(response.elapsed.total_seconds() * 1000)
    logger.info(
        f"external streaming API responded artist={artist} title={title} "
        f"sync_delay_ms={sync_delay_ms} metadata={metadata}"
    )

    return {
        "track": title,
        "artist": artist,
        **metadata,
        "sync_delay_ms": sync_delay_ms,
    }
