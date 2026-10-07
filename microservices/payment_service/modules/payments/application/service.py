from modules.payments.domain.models import Payment
from modules.payments.infrastructure.repository import PaymentRepository
from pydantic import BaseModel


class PaymentCreateDTO(BaseModel):
    lesson_id: int
    amount: float

class PaymentService:
    def __init__(self, repo: PaymentRepository):
        self.repo = repo

    def create_payment(self, dto: PaymentCreateDTO) -> Payment:
        """
        Метод координації бізнес-процесу створення платежу.
        Виконує мапінг DTO -> Domain модель (п. 5 завдання).
        """
        # Створюємо "чисту" доменну модель (Domain Layer)
        # Вона не залежить від SQLAlchemy (п. 4 завдання)
        new_payment = Payment(
            id=None,
            lesson_id=dto.lesson_id,
            amount=dto.amount,
            status="pending" # Бізнес-логіка: новий платіж завжди в статусі очікування
        )

        return self.repo.save(new_payment)