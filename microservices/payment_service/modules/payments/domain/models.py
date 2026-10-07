from dataclasses import dataclass
from typing import Optional

@dataclass
class Payment:
    id: Optional[int]
    lesson_id: int
    amount: float
    status: str = "pending"