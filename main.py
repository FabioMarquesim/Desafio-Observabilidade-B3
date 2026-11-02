from __future__ import annotations

import json
import logging
import os
import random
import threading
import time
from collections import deque
from pathlib import Path
from typing import Callable, Deque, Optional, Tuple

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"
SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "blockbuster-premiere-rush")

# Estado do Rush controlado pelos novos endpoints
RUSH_STATE = {
    "active": False,
    "error_mode": False,
    "start_time": None
}

class StrictJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": SERVICE_NAME,
        }
        span = trace.get_current_span()
        ctx = span.get_span_context() if span is not None else None
        if ctx is not None and ctx.is_valid:
            payload["trace_id"] = format(ctx.trace_id, "032x")
            payload["span_id"] = format(ctx.span_id, "016x")
        for key in ("user_id", "movie_id", "authorized", "resolution", "server_region", "error_type", "http_status"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, ensure_ascii=False)

def configure_logging() -> logging.Logger:
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(StrictJsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(stdout_handler)
    root.setLevel(logging.INFO)
    return logging.getLogger(SERVICE_NAME)

logger = configure_logging()

REQUEST_COUNT = Counter("http_requests_total", "Total requests", ["method", "endpoint", "status_code"])
REQUEST_ERRORS = Counter("http_request_errors_total", "Total errors", ["method", "endpoint", "status_code"])
REQUEST_DURATION = Histogram("http_request_duration_seconds", "Duration", ["method", "endpoint"])

class LoadMonitor:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._in_flight = 0
        self._timestamps: Deque[float] = deque()

    def register_request(self) -> Tuple[int, float]:
        now = time.monotonic()
        with self._lock:
            self._in_flight += 1
            self._timestamps.append(now)
            self._prune(now)
            rps = len(self._timestamps) / 1.0
            return self._in_flight, rps

    def release_request(self) -> None:
        now = time.monotonic()
        with self._lock:
            self._in_flight = max(0, self._in_flight - 1)
            self._prune(now)

    def snapshot(self) -> Tuple[int, float]:
        now = time.monotonic()
        with self._lock:
            self._prune(now)
            rps = len(self._timestamps) / 1.0
            return self._in_flight, rps

    def _prune(self, now: float) -> None:
        cutoff = now - 1.0
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()

load_monitor = LoadMonitor()

app = FastAPI(title="Blockbuster Premiere Rush", version="1.0.0")

@app.middleware("http")
async def red_metrics_middleware(request: Request, call_next: Callable):
    if request.url.path == "/metrics":
        return await call_next(request)
    method = request.method
    endpoint = request.url.path
    start = time.perf_counter()
    
    try:
        response = await call_next(request)
    except Exception:
        duration = time.perf_counter() - start
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code="500").inc()
        REQUEST_ERRORS.labels(method=method, endpoint=endpoint, status_code="500").inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        raise

    duration = time.perf_counter() - start
    status_code = str(response.status_code)
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
    if response.status_code >= 400:
        REQUEST_ERRORS.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    return response

@app.get("/")
def root():
    index = FRONTEND_DIR / "index.html"
    if index.is_file():
        return FileResponse(index, media_type="text/html; charset=utf-8")
    return {"message": "Blockbuster Premiere Rush API"}

# --- Endpoints de Controle ---
@app.post("/rush/start")
def start_rush():
    RUSH_STATE["active"] = True
    RUSH_STATE["error_mode"] = False
    RUSH_STATE["start_time"] = time.time()
    logger.info("Rush LIMPO iniciado (Sem erros)")
    return {"status": "started_clean", "timestamp": RUSH_STATE["start_time"]}

@app.post("/rush/error-start")
def start_rush_with_errors():
    RUSH_STATE["active"] = True
    RUSH_STATE["error_mode"] = True
    RUSH_STATE["start_time"] = time.time()
    logger.info("Rush COM ERROS iniciado (Chaos Mode)")
    return {"status": "started_with_errors", "timestamp": RUSH_STATE["start_time"]}

@app.post("/rush/stop")
def stop_rush():
    RUSH_STATE["active"] = False
    RUSH_STATE["error_mode"] = False
    RUSH_STATE["start_time"] = None
    logger.info("Rush finalizado/interrompido")
    return {"status": "stopped"}

@app.get("/stream/authorize")
def authorize_stream(
    user_id: str = Query(..., description="ID do usuário"),
    movie_id: str = Query(..., description="ID do filme"),
    force_resolution: Optional[str] = Query(None, description="Forçar resolução"),
):
    concurrent, rps = load_monitor.register_request()
    
    try:
        if not RUSH_STATE["active"]:
            resolution = "4K"
            load_level = "idle"
            status = "ok"
        else:
            current_time = time.time()
            elapsed = current_time - RUSH_STATE["start_time"]
            cycle_elapsed = elapsed % 90
            
            # Se o modo de erros estiver ativo, injeta falhas frequentes (15% de chance)
            if RUSH_STATE["error_mode"] and random.random() < 0.15:
                logger.error(
                    "Chaos mode simulated server error",
                    extra={
                        "user_id": user_id, 
                        "movie_id": movie_id, 
                        "error_type": "ChaosEngineeringFault", 
                        "http_status": 500
                    }
                )
                raise HTTPException(status_code=500, detail="Simulated chaotic stream authorization error")

            if cycle_elapsed < 30:
                resolution = "4K"
                load_level = "low"
                status = "ok"
            elif cycle_elapsed < 60:
                resolution = "1080p"
                load_level = "medium"
                status = "degraded"
            else:
                resolution = "720p"
                load_level = "high"
                status = "degraded"

        if force_resolution and force_resolution.upper() in ["4K", "1080P", "720P"]:
            resolution = force_resolution.upper()
            load_level = "manual_override"

        current_concurrent, current_rps = load_monitor.snapshot()

        decision = {
            "user_id": user_id,
            "movie_id": movie_id,
            "authorized": True,
            "resolution": resolution,
            "drm_token": "eyJhbGciOiJIUzI1NiIsInR5c...",
            "server_region": "sa-east-1",
            "status": status,
            "load_level": load_level,
            "concurrent_requests": current_concurrent,
            "requests_per_second": round(current_rps, 2),
            "rush_active": RUSH_STATE["active"],
            "error_mode": RUSH_STATE["error_mode"]
        }

        return decision

    finally:
        load_monitor.release_request()

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

FastAPIInstrumentor.instrument_app(app, excluded_urls="metrics")