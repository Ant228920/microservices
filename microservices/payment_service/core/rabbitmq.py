import json
import os

import pika
from core.config import settings

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "payment_events")


def publish_event(payload: dict):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=settings.rabbitmq_host, port=settings.rabbitmq_port)
    )
    channel = connection.channel()

    channel.queue_declare(queue=settings.rabbitmq_queue)

    channel.basic_publish(
        exchange='',
        routing_key=settings.rabbitmq_queue,  # 👈 Повідомлення має йти саме сюди!
        body=json.dumps(payload)
    )
    connection.close()