import json
import logging

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.view import ExponentialBucketHistogramAggregation, View
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

SERVICE_NAME = "live-sync-api"


class JsonTraceFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        span_context = trace.get_current_span().get_span_context()
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": format(span_context.trace_id, "032x") if span_context.trace_id else None,
            "span_id": format(span_context.span_id, "016x") if span_context.span_id else None,
        }
        return json.dumps(payload)


def setup_telemetry() -> None:
    resource = Resource.create({"service.name": SERVICE_NAME})

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(tracer_provider)

    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JsonTraceFormatter())

    otlp_handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)

    logging.basicConfig(level=logging.INFO, handlers=[console_handler, otlp_handler])

    native_duration_view = View(
        instrument_name="http.server.request.duration",
        aggregation=ExponentialBucketHistogramAggregation(),
    )

    meter_provider = MeterProvider(
        resource=resource,
        views=[native_duration_view],
    )
    metrics.set_meter_provider(meter_provider)
