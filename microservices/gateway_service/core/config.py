from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PORT: int = 8000

    # Internal service URLs (Docker network names)
    USER_SERVICE_URL: str = "http://user_service:8001"
    PAYMENT_SERVICE_URL: str = "http://payment_service:8002"

    # Timeouts (seconds)
    HTTP_TIMEOUT: float = 5.0

    class Config:
        env_file = ".env_gateway"


settings = Settings()