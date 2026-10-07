import json
import time

import pika
from core.config import settings
from pika.exceptions import AMQPConnectionError


def start_consumer():
    connection = None
    while not connection:
        try:
            print(f"🔄 Спроба підключення до RabbitMQ на {settings.rabbitmq_host}:{settings.rabbitmq_port}...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=settings.rabbitmq_host, port=settings.rabbitmq_port)
            )
        except AMQPConnectionError:
            print("⏳ RabbitMQ ще завантажується. Чекаємо 3 секунди...")
            time.sleep(3)

    print("✅ Успішно підключено до RabbitMQ!")
    channel = connection.channel()

    # Оголошуємо чергу, яку слухаємо (події від Payment)
    channel.queue_declare(queue=settings.rabbitmq_queue)

    # 👇 Оголошуємо чергу для відповідей (щоб повернути статус у Payment)
    reply_queue = "payment_responses"
    channel.queue_declare(queue=reply_queue)

    def callback(ch, method, properties, body):
        try:
            data = json.loads(body)
            payment_id = data.get("payment_id")
            lesson_id = data.get("lesson_id")

            print("\n" + "!" * 60)
            print(f"🚀 USER SERVICE ОТРИМАВ ЗАПИТ НА ПЛАТІЖ №{payment_id}")

            if lesson_id == 0:
                status = "failed"
                reason = "Tutor is busy"
                print(f"❌ Помилка: Репетитор для уроку {lesson_id} зайнятий.")
            else:
                status = "success"
                reason = "Tutor assigned"
                print(f"✅ Успіх: Репетитор підтвердив урок {lesson_id}.")

            reply_message = {
                "payment_id": payment_id,
                "status": status,
                "reason": reason
            }

            ch.basic_publish(
                exchange='',
                routing_key=reply_queue,
                body=json.dumps(reply_message)
            )
            print(f"📤 Відповідь [{status}] надіслана в чергу {reply_queue}")
            print("!" * 60 + "\n")


        except Exception as e:  # noqa: BLE001
            print(f"❌ Помилка в Consumer: {e}")

    channel.basic_consume(
        queue=settings.rabbitmq_queue,
        on_message_callback=callback,
        auto_ack=True
    )

    print(f"[*] Очікування подій у черзі '{settings.rabbitmq_queue}'...")
    channel.start_consuming()