from sqlalchemy import Column, Integer, String
from core.database import Base

class UserTable(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String)
    email = Column(String, unique=True)
    role = Column(String)