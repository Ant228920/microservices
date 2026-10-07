import time
from sqlalchemy.orm import Session
from core.database import SessionLocal
from modules.payments.infrastructure.models import OutboxEventTable
from core.rabbitmq import publish_event


def relay():
    print("🚀 Фоновий процес Relay запущено. Очікування нових подій в Outbox...")

    while True:
        db: Session = SessionLocal()

        try:
            events = db.query(OutboxEventTable).filter(
                OutboxEventTable.is_processed == False
            ).all()

            for event in events:
                try:
                    print(f"📤 Знайдено неопрацьовану подію {event.id}. Спроба відправки...")

                    publish_event(event.payload)


                    event.is_processed = True
                    db.commit()

                    print(f"✅ Подія {event.id} успішно відправлена та позначена як is_processed=True!")

                except Exception as e:
                    print(f"❌ Помилка відправки події {event.id} у RabbitMQ: {e}")
                    db.rollback()

        except Exception as db_err:
            print(f"⚠️ Помилка доступу до БД у процесі Relay: {db_err}")

        finally:
            db.close()

        time.sleep(5)