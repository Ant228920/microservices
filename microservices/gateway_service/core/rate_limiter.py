import time
from collections import defaultdict
from fastapi import HTTPException

# Зберігаємо запити в пам'яті: {ip: [timestamp, ...]}
_request_log: dict[str, list[float]] = defaultdict(list)

RATE_LIMIT = 10        # максимум запитів
WINDOW_SECONDS = 60    # за цей проміжок часу


def check_rate_limit(ip: str):
    now = time.time()
    window_start = now - WINDOW_SECONDS

    # Прибираємо старі записи
    _request_log[ip] = [t for t in _request_log[ip] if t > window_start]

    if len(_request_log[ip]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Max {RATE_LIMIT} per {WINDOW_SECONDS}s.",
            headers={"Retry-After": str(WINDOW_SECONDS)},
        )

    _request_log[ip].append(now)