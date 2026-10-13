from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

from server.config import Settings


class Base(DeclarativeBase):
    pass


def make_engine(settings: Settings):
    return create_engine(settings.database_url.get_secret_value(), pool_pre_ping=True)
