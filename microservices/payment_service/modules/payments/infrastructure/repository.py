from sqlalchemy.orm import Session
from modules.payments.infrastructure.models import PaymentTable, OutboxEventTable
from modules.payments.domain.models import Payment


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, payment: Payment) -> Payment:
        try:
            db_payment = PaymentTable(
                lesson_id=payment.lesson_id,
                amount=payment.amount,
                status=payment.status
            )
            self.db.add(db_payment)
            self.db.flush()

            outbox_event = OutboxEventTable(
                aggregate_type="Payment",
                aggregate_id=str(db_payment.id),
                event_type="PaymentCreated",
                payload={
                    "payment_id": db_payment.id,
                    "lesson_id": db_payment.lesson_id,
                    "amount": db_payment.amount,
                    "status": db_payment.status
                }
            )
            self.db.add(outbox_event)
            self.db.commit()

            payment.id = db_payment.id
            return payment

        except Exception as e:
            self.db.rollback()
            print(f"❌ Помилка транзакції при збереженні платежу: {e}")
            raise

    # ← ТУТ, після save, на рівні класу
    def get_all(self):
        return self.db.query(PaymentTable).all()

    def get_by_id(self, payment_id: int):
        return self.db.query(PaymentTable).filter(PaymentTable.id == payment_id).first()