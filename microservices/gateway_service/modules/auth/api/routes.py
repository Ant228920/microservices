from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.auth import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

# Простий in-memory store для демонстрації
USERS_DB = {
    "admin": {"password": "admin123", "role": "admin", "id": 1},
    "user": {"password": "user123", "role": "user", "id": 2},
}


class LoginDTO(BaseModel):
    username: str
    password: str


class RegisterDTO(BaseModel):
    username: str
    password: str
    role: str = "user"


@router.post("/login", summary="Отримати JWT токен")
def login(dto: LoginDTO):
    user = USERS_DB.get(dto.username)
    if not user or user["password"] != dto.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": str(user["id"]),
        "username": dto.username,
        "role": user["role"],
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"],
    }


@router.post("/register", summary="Зареєструвати нового користувача")
def register(dto: RegisterDTO):
    if dto.username in USERS_DB:
        raise HTTPException(status_code=400, detail="User already exists")

    new_id = max(u["id"] for u in USERS_DB.values()) + 1
    USERS_DB[dto.username] = {
        "password": dto.password,
        "role": dto.role,
        "id": new_id,
    }
    token = create_access_token({
        "sub": str(new_id),
        "username": dto.username,
        "role": dto.role,
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": dto.role,
    }