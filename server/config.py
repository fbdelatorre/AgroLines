from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AGROLINES_", extra="ignore")
    app_name: str = "AgroLines"
    database_url: SecretStr = Field(default=SecretStr("postgresql+psycopg://localhost/agrolines"))

    access_ttl: int = Field(default=900, ge=60, le=3600)
    refresh_ttl: int = Field(default=86400, ge=3600, le=604800)
    login_limit: int = Field(default=10, ge=1, le=100)
    login_window: int = Field(default=900, ge=60)
    smtp_host: str | None = None
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_from: str = "agrolines@example.com"
    smtp_username: str | None = None
    smtp_password: SecretStr = SecretStr("")


@lru_cache
def get_settings() -> Settings:
    return Settings()
