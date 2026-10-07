import threading

from consumer import start_consumer
from fastapi import FastAPI
from modules.users.api.routes import router as users_router

# Якщо у тебе в user_service теж є своя база даних (наприклад, таблиця Users),
# то розкоментуй ці рядки, щоб вони теж створювалися автоматично:
# from core.database import engine, Base
# from modules.users.infrastructure.models import UserTable # заміни на свою модель
# Base.metadata.create_all(bind=engine)

# 👇 Налаштування Swagger для сервісу користувачів
app = FastAPI(
    title="User Service API",
    description="API мікросервісу користувачів (Асинхронний Consumer)",
    version="1.0.0"
)

app.include_router(users_router)

# Робимо запуск безпечним, так само як у payment_service
@app.on_event("startup")
def startup_event():
    print("🚀 Запуск FastAPI User Service...")
    threading.Thread(target=start_consumer, daemon=True).start()