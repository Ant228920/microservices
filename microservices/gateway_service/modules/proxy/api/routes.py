from core.config import settings
from core.http_client import safe_proxy
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()


async def _forward(request: Request, upstream_base: str, path: str) -> JSONResponse:
    query = f"?{request.url.query}" if request.url.query else ""
    url = f"{upstream_base}/{path}{query}"
    body = await request.body()
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length")
    }
    status, data = await safe_proxy(request.method, url, headers=headers, body=body)
    return JSONResponse(content=data, status_code=status)


# ── Users ──────────────────────────────────────────
@router.get("/users/", summary="Proxy → GET всі юзери")
async def proxy_get_users(request: Request):
    return await _forward(request, settings.USER_SERVICE_URL, "users/")


@router.get("/users/{user_id}", summary="Proxy → GET юзер по ID")
async def proxy_get_user(user_id: int, request: Request):
    return await _forward(request, settings.USER_SERVICE_URL, f"users/{user_id}")


@router.post("/users/", summary="Proxy → POST створити юзера")
async def proxy_create_user(request: Request):
    return await _forward(request, settings.USER_SERVICE_URL, "users/")


# ── Payments ───────────────────────────────────────
@router.get("/payments/", summary="Proxy → GET всі платежі")
async def proxy_get_payments(request: Request):
    return await _forward(request, settings.PAYMENT_SERVICE_URL, "payments/")


@router.get("/payments/{payment_id}", summary="Proxy → GET платіж по ID")
async def proxy_get_payment(payment_id: int, request: Request):
    return await _forward(request, settings.PAYMENT_SERVICE_URL, f"payments/{payment_id}")


@router.post("/payments/", summary="Proxy → POST створити платіж")
async def proxy_create_payment(request: Request):
    return await _forward(request, settings.PAYMENT_SERVICE_URL, "payments/")