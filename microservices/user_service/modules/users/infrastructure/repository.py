from sqlalchemy.orm import Session
from .models import UserTable
from ..domain.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, user: User) -> User:
        db_user = UserTable(
            fullname=user.fullname,
            email=user.email,
            role=user.role
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        user.id = db_user.id
        return user

    def get(self, user_id: int):
        db_user = self.db.query(UserTable).filter(UserTable.id == user_id).first()
        if not db_user:
            return None

        return User(
            id=db_user.id,
            fullname=db_user.fullname,
            email=db_user.email,
            role=db_user.role
        )