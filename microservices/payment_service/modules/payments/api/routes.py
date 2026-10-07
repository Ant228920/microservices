import uuid

import pybreaker
from core.database import get_db
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..application.service import PaymentCreateDTO, PaymentService
from ..infrastructure.repository import PaymentRepository
from ..infrastructure.user_client import UserNotFoundException, get_user

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/")
def list_payments(db: Session = Depends(get_db)):  # noqa: B008
    repo = PaymentRepository(db)
    return repo.get_all()


@router.post("/", status_code=201)
def create_payment(dto: PaymentCreateDTO, db: Session = Depends(get_db)):  # noqa: B008
    try:
        repo = PaymentRepository(db)
        service = PaymentService(repo)
        return service.create_payment(dto)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}")
def get_payment(user_id: int, request: Request):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))

    try:
        user = get_user(user_id, correlation_id)
        return {
            "user": user,
            "payment": "ok",
            "correlation_id": correlation_id
        }

    except UserNotFoundException:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "User not found",
                "correlation_id": correlation_id
            }
        )

    except pybreaker.CircuitBreakerError:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "User service unavailable (circuit open)",
                "fallback": True,
                "correlation_id": correlation_id
            }
        )

    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=503,
            detail={
                "error": "User service unavailable",
                "fallback": True,
                "correlation_id": correlation_id
            }
        )