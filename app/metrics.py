import time

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

# R (Rate) e E (Errors): contador por método, rota e status
REQUESTS = Counter(
    "stream_api_http_requests_total",
    "Total de requisições HTTP",
    ["method", "route", "status"],
)

# D (Duration): histograma de latência em segundos
DURATION = Histogram(
    "stream_api_http_request_duration_seconds",
    "Duração das requisições HTTP em segundos",
    ["method", "route"],
    buckets=(0.05, 0.1, 0.15, 0.25, 0.3, 0.4, 0.5, 0.75, 1.0, 2.5),
)


def setup_metrics(app: FastAPI) -> None:
    @app.middleware("http")
    async def track_requests(request: Request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)

        start = time.perf_counter()
        status = 500  # se ocorrer exceção não tratada, conta como 500
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        finally:
            elapsed = time.perf_counter() - start
            route = request.scope.get("route")
            path = route.path if route else "unmatched"
            REQUESTS.labels(request.method, path, str(status)).inc()
            DURATION.labels(request.method, path).observe(elapsed)

    @app.get("/metrics", include_in_schema=False)
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)