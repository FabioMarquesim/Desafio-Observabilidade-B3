from __future__ import annotations

import json
import logging
import os
import random
import threading
import time
import uuid
from collections import deque
from pathlib import Path
from typing import Callable, Deque, Optional, Tuple

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"
SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "blockbuster-premiere-rush")

# Configuração explícita do OpenTelemetry TracerProvider para exportar para o Tempo (OTLP gRPC)
resource = Resource.create(attributes={"service.name": SERVICE_NAME})
provider = TracerProvider(resource=resource)
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-lgtm:4317")
exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

# Estado do Rush controlado pelos endpoints de controlo
RUSH_STATE = {
    "active": False,
    "error_mode": False,
    "start_time": None
}

class StrictJsonFormatter(logging.Formatter):
    """Formatador personalizado para estruturar logs em JSON com trace_id hexadecimal limpo."""
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": SERVICE_NAME,
        }
        
        trace_id = getattr(record, "trace_id", None)
        span_id = getattr(record, "span_id", None)
        
        if not trace_id or trace_id == "0" * 32 or set(trace_id) <= {"a", "0"}:
            span = trace.get_current_span()
            ctx = span.get_span_context() if span is not None else None
            if ctx is not None and ctx.is_valid and ctx.trace_id != trace.INVALID_TRACE_ID:
                trace_id = format(ctx.trace_id, "032x")
                span_id = format(ctx.span_id, "016x")
            else:
                clean_uuid = uuid.uuid4().hex
                trace_id = clean_uuid
                span_id = clean_uuid[:16]

        payload["trace_id"] = trace_id
        payload["span_id"] = span_id
        
        # Atributos extra passados nos logs
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

# Métricas RED (Rate, Errors, Duration)
REQUEST_COUNT = Counter("http_requests_total", "Total requests", ["method", "endpoint", "status_code"])
REQUEST_ERRORS = Counter("http_request_errors_total", "Total errors", ["method", "endpoint", "status_code"])
REQUEST_DURATION = Histogram("http_request_duration_seconds", "Duration", ["method", "endpoint"])

class LoadMonitor:
    """Monitor de concorrência e requisições por segundo (RPS)."""
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
async def red_metrics_and_trace_middleware(request: Request, call_next: Callable):
    """Middleware integrado para métricas RED e propagação rigorosa de rastreio."""
    if request.url.path == "/metrics":
        return await call_next(request)
        
    method = request.method
    endpoint = request.url.path
    start = time.perf_counter()
    
    span = trace.get_current_span()
    ctx = span.get_span_context() if span is not None else None
    if ctx is not None and ctx.is_valid and ctx.trace_id != trace.INVALID_TRACE_ID:
        t_id = format(ctx.trace_id, "032x")
        s_id = format(ctx.span_id, "016x")
    else:
        clean_uuid = uuid.uuid4().hex
        t_id = clean_uuid
        s_id = clean_uuid[:16]

    request.state.trace_id = t_id
    request.state.span_id = s_id

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

# --- Endpoints de Controlo do Rush e Caos ---
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
async def authorize_stream(
    request: Request,
    user_id: str = Query(..., description="ID do usuário"),
    movie_id: str = Query(..., description="ID do filme"),
    force_resolution: Optional[str] = Query(None, description="Forçar resolução"),
):
    concurrent, rps = load_monitor.register_request()
    
    t_id = getattr(request.state, "trace_id", uuid.uuid4().hex)
    s_id = getattr(request.state, "span_id", t_id[:16])

    try:
        if not RUSH_STATE["active"]:
            resolution = "4K"
            load_level = "idle"
            status = "ok"
        else:
            current_time = time.time()
            elapsed = current_time - RUSH_STATE["start_time"]
            cycle_elapsed = elapsed % 90
            
            if RUSH_STATE["error_mode"] and random.random() < 0.15:
                logger.error(
                    "Chaos mode simulated server error",
                    extra={
                        "user_id": user_id, 
                        "movie_id": movie_id, 
                        "error_type": "ChaosEngineeringFault", 
                        "http_status": 500,
                        "trace_id": t_id,
                        "span_id": s_id
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

        logger.info(
            "Stream authorized successfully",
            extra={
                "user_id": user_id,
                "movie_id": movie_id,
                "resolution": resolution,
                "http_status": 200,
                "trace_id": t_id,
                "span_id": s_id
            }
        )

        return decision

    finally:
        load_monitor.release_request()

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Instrumentação automática do FastAPI para OpenTelemetry Tracing
FastAPIInstrumentor.instrument_app(app, excluded_urls="metrics")