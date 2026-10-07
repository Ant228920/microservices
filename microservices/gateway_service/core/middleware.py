import time
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.auth import PUBLIC_PATHS, decode_token, extract_token
from core.rate_limiter import check_rate_limit
from core.metrics import REQUEST_COUNT, REQUEST_LATENCY, ERROR_COUNT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("gateway")


class GatewayMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        path = request.url.path
        method = request.method
        client_ip = request.client.host if request.client else "unknown"

        # ── 1. Rate Limiting ──────────────────────────────
        try:
            check_rate_limit(client_ip)
        except Exception as e:
            logger.warning(f"[RATE LIMIT] {client_ip} → {method} {path}")
            ERROR_COUNT.labels(method=method, path=path, status_code=429).inc()
            REQUEST_COUNT.labels(method=method, path=path, status_code=429).inc()
            return JSONResponse(status_code=429, content={"detail": str(e)})

        # ── 2. Auth (пропускаємо публічні шляхи) ─────────
        user_payload = None
        if path not in PUBLIC_PATHS:
            token = extract_token(request)
            if not token:
                logger.warning(f"[AUTH] No token → {method} {path} from {client_ip}")
                ERROR_COUNT.labels(method=method, path=path, status_code=401).inc()
                REQUEST_COUNT.labels(method=method, path=path, status_code=401).inc()
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Authorization token required"}
                )
            try:
                user_payload = decode_token(token)
            except Exception:
                logger.warning(f"[AUTH] Invalid token → {method} {path} from {client_ip}")
                ERROR_COUNT.labels(method=method, path=path, status_code=401).inc()
                REQUEST_COUNT.labels(method=method, path=path, status_code=401).inc()
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid or expired token"}
                )

        # ── 3. Прокидаємо контекст безпеки далі ──────────
        if user_payload:
            request.state.user_id = user_payload.get("sub")
            request.state.user_role = user_payload.get("role", "user")

        # ── 4. Виконуємо запит ────────────────────────────
        response = await call_next(request)
        duration = time.time() - start_time
        status_code = response.status_code

        # ── 5. Метрики ────────────────────────────────────
        REQUEST_COUNT.labels(method=method, path=path, status_code=status_code).inc()
        REQUEST_LATENCY.labels(method=method, path=path).observe(duration)
        if status_code >= 400:
            ERROR_COUNT.labels(method=method, path=path, status_code=status_code).inc()

        # ── 6. Логування ──────────────────────────────────
        user_info = f"user={user_payload.get('sub')}" if user_payload else "anonymous"
        logger.info(
            f"[{method}] {path} | {status_code} | {duration:.3f}s | {client_ip} | {user_info}"
        )

        return response