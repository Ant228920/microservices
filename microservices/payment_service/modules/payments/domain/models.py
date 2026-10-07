from dataclasses import dataclass


@dataclass
class Payment:
    id: int | None
    lesson_id: int
    amount: float
    status: str = "pending"