import json
import logging
import sys
from datetime import datetime, timezone

from opentelemetry import trace

# Campos extras que a gente passa nos logs da rota
EXTRA_FIELDS = ("user_id", "movie_id", "resolution", "latency_ms")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        ctx = trace.get_current_span().get_span_context()

        log = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": format(ctx.trace_id, "032x") if ctx.is_valid else "",
            "span_id": format(ctx.span_id, "016x") if ctx.is_valid else "",
        }

        for field in EXTRA_FIELDS:
            if hasattr(record, field):
                log[field] = getattr(record, field)

        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)

        return json.dumps(log, ensure_ascii=False)


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)