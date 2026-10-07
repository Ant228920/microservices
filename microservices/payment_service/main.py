from fastapi import FastAPI
from modules.payments.api.routes import router as payments_router
import threading
from consumer import start_payment_consumer
from core.relay import relay

# Додаємо імпорти для створення бази даних
from core.database import engine, Base
from modules.payments.infrastructure.models import PaymentTable, OutboxEventTable

# Цей рядок автоматично створить таблицю payments та outbox_events при запуску!
Base.metadata.create_all(bind=engine)

# 👇 Робимо Swagger красивим та інформативним
app = FastAPI(
    title="Payment Service API",
    description="API для створення платежів та демонстрації патерну Transactional Outbox",
    version="1.0.0",
    docs_url="/docs" # За замовчуванням Swagger лежить тут
)

app.include_router(payments_router)

@app.on_event("startup")
def start_background_tasks():
    print("🚀 Запуск фонових процесів Payment Service...")
    threading.Thread(target=relay, daemon=True).start()
    threading.Thread(target=start_payment_consumer, daemon=True).start()

@app.on_event("startup")
def start_relay():
    print("🚀 Запуск FastAPI Payment Service...")
    threading.Thread(target=relay, daemon=True).start()