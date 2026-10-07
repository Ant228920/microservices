from dataclasses import dataclass


@dataclass
class User:
    id: int | None
    fullname: str
    email: str
    role: str