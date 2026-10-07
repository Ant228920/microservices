from core.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..application.service import UserCreateDTO, UserService
from ..infrastructure.repository import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/")
def create_user(dto: UserCreateDTO, db: Session = Depends(get_db)):  # noqa: B008
    service = UserService(UserRepository(db))
    return service.register(dto)


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):  # noqa: B008
    service = UserService(UserRepository(db))
    user = service.get_user(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user