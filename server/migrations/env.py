from alembic import context

from server import models  # noqa: F401 — register migration metadata
from server.config import get_settings
from server.db import Base, make_engine


def include_object(obj, name, kind, reflected, compare_to):
    # Never generate implicit drops for PostGIS or other externally managed tables.
    return not (kind == "table" and reflected and compare_to is None)


def include_name(name, kind, parent_names):
    return kind != "table" or name in Base.metadata.tables


if context.is_offline_mode():
    context.configure(
        url=get_settings().database_url.get_secret_value(),
        target_metadata=Base.metadata,
        include_object=include_object,
        include_name=include_name,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = make_engine(get_settings())
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
            include_object=include_object,
            include_name=include_name,
        )
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()
