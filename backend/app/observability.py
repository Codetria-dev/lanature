import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse

try:
    import sentry_sdk
except ImportError:  # pragma: no cover - optional dependency
    sentry_sdk = None

try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
except ImportError:  # pragma: no cover - optional dependency
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4"
    Counter = None
    Histogram = None
    generate_latest = None


REQUEST_COUNT = (
    Counter(
        "lanature_http_requests_total",
        "Total HTTP requests",
        ["method", "path", "status"],
    )
    if Counter
    else None
)
REQUEST_LATENCY = (
    Histogram(
        "lanature_http_request_latency_seconds",
        "HTTP request latency in seconds",
        ["method", "path"],
    )
    if Histogram
    else None
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_id"):
            payload["request_id"] = record.request_id
        if hasattr(record, "path"):
            payload["path"] = record.path
        if hasattr(record, "method"):
            payload["method"] = record.method
        if hasattr(record, "status_code"):
            payload["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            payload["duration_ms"] = record.duration_ms
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=True)


def configure_logging() -> None:
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root.handlers = [handler]


def configure_sentry() -> None:
    if sentry_sdk is None:
        return
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return
    traces_sample_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.2"))
    sentry_sdk.init(
        dsn=dsn,
        traces_sample_rate=traces_sample_rate,
        environment=os.getenv("ENVIRONMENT", "development"),
    )


def add_observability(app: FastAPI) -> None:
    logger = logging.getLogger("lanature.api")

    @app.middleware("http")
    async def metrics_and_logging_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start = time.perf_counter()
        path = request.url.path
        method = request.method

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.exception(
                "Unhandled request error",
                extra={
                    "request_id": request_id,
                    "path": path,
                    "method": method,
                    "status_code": 500,
                    "duration_ms": duration_ms,
                },
            )
            if REQUEST_COUNT is not None:
                REQUEST_COUNT.labels(method=method, path=path, status="500").inc()
            if REQUEST_LATENCY is not None:
                REQUEST_LATENCY.labels(method=method, path=path).observe(duration_ms / 1000)
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        if REQUEST_COUNT is not None:
            REQUEST_COUNT.labels(method=method, path=path, status=str(status_code)).inc()
        if REQUEST_LATENCY is not None:
            REQUEST_LATENCY.labels(method=method, path=path).observe(duration_ms / 1000)
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "path": path,
                "method": method,
                "status_code": status_code,
                "duration_ms": duration_ms,
            },
        )
        return response

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> PlainTextResponse:
        if generate_latest is None:
            return JSONResponse(status_code=503, content={"detail": "prometheus-client not installed"})
        return PlainTextResponse(generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)
