from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "FleetCore"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    DEFAULT_LANGUAGE: str = "ru"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://fleetcore:fleetcore@localhost:5432/fleetcore"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://fleetcore:fleetcore@localhost:5432/fleetcore"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # MinIO / S3
    MINIO_ENDPOINT: str = "localhost:9002"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "fleetcore"
    MINIO_USE_SSL: bool = False

    # SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@fleetcore.local"

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 200

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
