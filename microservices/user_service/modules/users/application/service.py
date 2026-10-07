from pydantic import BaseModel, EmailStr

from ..domain.models import User


class UserCreateDTO(BaseModel):
    fullname: str
    email: EmailStr
    role: str


class UserService:
    def __init__(self, repo):
        self.repo = repo

    def register(self, dto: UserCreateDTO):
        user = User(
            id=None,
            fullname=dto.fullname,
            email=dto.email,
            role=dto.role
        )
        return self.repo.save(user)

    def get_user(self, user_id: int):
        return self.repo.get(user_id)