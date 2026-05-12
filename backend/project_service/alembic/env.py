"""
Alembic environment configuration.

Key decisions:
    1. DATABASE_URL comes from app.core.config.settings — never from alembic.ini.
       This means the same .env file controls both the app and migrations.

    2. All model modules are imported before target_metadata is set.
       Alembic's autogenerate compares Base.metadata against the live DB.
       If a model file is NOT imported here, its table is invisible to Alembic
       and will be silently dropped on the next `alembic upgrade head`.

    3. compare_type=True: detects column type changes (e.g. String(100) → String(255)).
       Without this, Alembic ignores type-only changes.
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# ── Load app config ───────────────────────────────────────────────────────────
from app.core.config import settings

# ── Import ALL models so Base.metadata is fully populated ────────────────────
from app.db.base import Base
from app.models import project  # noqa: F401 — import triggers model registration

target_metadata = Base.metadata

# ── Alembic Config object ─────────────────────────────────────────────────────
config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    """
    Run migrations without a live DB connection.
    Useful for generating SQL scripts to review before applying.
    """
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations against a live DB connection.
    Used by `alembic upgrade head` in CI/CD and local dev.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
