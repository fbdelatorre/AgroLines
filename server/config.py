from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AGROLINES_", extra="ignore")
    app_name: str = "AgroLines"
    database_url: SecretStr = Field(default=SecretStr("postgresql+psycopg://localhost/agrolines"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
