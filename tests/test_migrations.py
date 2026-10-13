from io import StringIO

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

from server.config import get_settings


def test_additive_migration_sql_and_revision_chain(monkeypatch):
    monkeypatch.setenv("AGROLINES_DATABASE_URL", "postgresql+psycopg://localhost/agrolines")
    get_settings.cache_clear()
    output = StringIO()
    config = Config("alembic.ini", output_buffer=output)
    assert ScriptDirectory.from_config(config).get_current_head() == "0002"
    command.upgrade(config, "head", sql=True)
    sql = output.getvalue()
    for table in (
        "users",
        "credentials",
        "sessions",
        "farms",
        "seasons",
        "operations",
        "invitations",
        "permissions",
        "audit_events",
        "refresh_tokens",
        "password_resets",
    ):
        assert f"CREATE TABLE {table}" in sql
    assert "CREATE EXTENSION IF NOT EXISTS postgis" in sql
    assert "DROP TABLE" not in sql
    assert "DELETE FROM" not in sql
    assert "'0002'" in sql
    get_settings.cache_clear()
