import pika
import json
import time
from pika.exceptions import AMQPConnectionError
from core.config import settings
from core.database import SessionLocal
from modules.payments.infrastructure.models import PaymentTable


def start_payment_consumer():
    connection = None
    # 1. Ретрай-механізм підключення
    while not connection:
        try:
            print(f"🔄 Payment Consumer: Спроба підключення до RabbitMQ...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=settings.rabbitmq_host, port=settings.rabbitmq_port)
            )
        except AMQPConnectionError:
            print("⏳ RabbitMQ ще завантажується. Чекаємо 3 секунди...")
            time.sleep(3)

    print("✅ Payment Consumer успішно підключено!")
    channel = connection.channel()

    # 2. Оголошуємо ту саму чергу відповідей, яку ми прописали в User Service
    reply_queue = "payment_responses"
    channel.queue_declare(queue=reply_queue)

    # 3. Функція-обробник відповіді
    def callback(ch, method, properties, body):
        db = SessionLocal()
        try:
            data = json.loads(body)
            payment_id = data.get("payment_id")
            status = data.get("status")  # success або failed

            print(f"\n📩 ОТРИМАНО ВІДПОВІДЬ ДЛЯ ПЛАТЕЖУ №{payment_id}: {status}")

            # Шукаємо платіж у базі
            payment = db.query(PaymentTable).filter(PaymentTable.id == payment_id).first()

            if payment:
                if status == "success":
                    payment.status = "confirmed"
                    print(f"✅ Статус платежу №{payment_id} змінено на CONFIRMED")
                else:
                    # ЦЕ І Є КОМПЕНСАЦІЙНА ТРАНЗАКЦІЯ
                    payment.status = "rejected"
                    print(f"⚠️ КОМПЕНСАЦІЯ: Статус платежу №{payment_id} змінено на REJECTED")

                db.commit()
            else:
                print(f"❓ Платіж №{payment_id} не знайдено в базі")

        except Exception as e:
            print(f"❌ Помилка обробки відповіді: {e}")
            db.rollback()
        finally:
            db.close()

    # 4. Підписка на чергу відповідей
    channel.basic_consume(
        queue=reply_queue,
        on_message_callback=callback,
        auto_ack=True
    )

    print(f"[*] Очікування відповідей у черзі '{reply_queue}'...")
    channel.start_consuming()