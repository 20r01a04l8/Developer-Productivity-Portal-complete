import json
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Application ───────────────────────────────────────────────────────────
    APP_NAME: str = "project-service"
    APP_ENV: str = "development"
    APP_PORT: int = 8001
    # Named APP_DEBUG (not DEBUG) to avoid collision with the Windows system
    # environment variable DEBUG=release which causes a pydantic bool parse error
    APP_DEBUG: bool = True

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str                  # required — no default forces explicit config
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # ── JWT ───────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str                # required — no default forces explicit config
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        # .env stores this as a JSON string: ["http://localhost:3000"]
        # pydantic-settings reads it as a plain string, so we parse it manually
        if isinstance(v, str):
            return json.loads(v)
        return v

    class Config:
        env_file = ".env"


# Single shared instance imported everywhere as:
#   from app.core.config import settings
settings = Settings()
