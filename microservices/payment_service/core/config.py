from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    app_port: int = 8000
    app_host: str = "127.0.0.1"
    app_debug: bool = False
    secret_key: str = "default_secret"

    # ДОДАНІ ЗМІННІ ДЛЯ RABBITMQ:
    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_queue: str

    class Config:
        env_file = ".env_payment"
        # Цей рядок каже Pydantic ігнорувати будь-які інші змінні в .env,
        # яких немає в цьому класі, щоб додаток більше не падав через такі дрібниці:
        extra = "ignore"

settings = Settings()