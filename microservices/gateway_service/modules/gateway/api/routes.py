import asyncio
import httpx
from fastapi import APIRouter, HTTPException, Path
from core.config import settings
from core.http_client import safe_get

router = APIRouter()


@router.get("/payment-details/{user_id}")
async def get_payment_details(user_id: int = Path(...)):
    async with httpx.AsyncClient() as client:
        user, payments = await asyncio.gather(
            safe_get(client, f"{settings.USER_SERVICE_URL}/users/{user_id}"),
            safe_get(client, f"{settings.PAYMENT_SERVICE_URL}/payments/"),
        )

    if user is None and payments is None:
        raise HTTPException(status_code=503, detail="All services unavailable")

    return {
        "user_id": user_id,
        "user": user,
        "payments": payments,
        "meta": {
            "user_service_available": user is not None,
            "payment_service_available": payments is not None,
        }
    }


@router.get("/user-payments/{user_id}")
async def get_user_payments(user_id: int = Path(...)):
    async with httpx.AsyncClient() as client:
        user, payments = await asyncio.gather(
            safe_get(client, f"{settings.USER_SERVICE_URL}/users/{user_id}"),
            safe_get(client, f"{settings.PAYMENT_SERVICE_URL}/payments/"),
        )

    if user is None and payments is None:
        raise HTTPException(status_code=503, detail="All services unavailable")

    return {
        "user_id": user_id,
        "user": user,
        "payments": payments,
        "meta": {
            "user_service_available": user is not None,
            "payment_service_available": payments is not None,
        }
    }