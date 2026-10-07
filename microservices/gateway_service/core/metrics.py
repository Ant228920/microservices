from fastapi import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

# Кількість запитів
REQUEST_COUNT = Counter(
    "gateway_requests_total",
    "Total number of requests",
    ["method", "path", "status_code"]
)

# Латентність
REQUEST_LATENCY = Histogram(
    "gateway_request_duration_seconds",
    "Request duration in seconds",
    ["method", "path"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

# Помилки
ERROR_COUNT = Counter(
    "gateway_errors_total",
    "Total number of errors",
    ["method", "path", "status_code"]
)


def metrics_endpoint():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )