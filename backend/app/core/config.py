from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "SIEM Security Tool"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./siem.db"

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # ML Settings
    ANOMALY_DETECTION_THRESHOLD: float = 0.7
    MODEL_RETRAIN_INTERVAL_HOURS: int = 24

    # Log Retention
    LOG_RETENTION_DAYS: int = 90

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
