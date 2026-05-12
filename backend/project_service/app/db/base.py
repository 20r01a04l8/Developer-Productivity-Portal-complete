from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    All SQLAlchemy models inherit from this single Base.
    Alembic's env.py imports Base.metadata to auto-detect all tables.
    Every model file must be imported in alembic/env.py for detection to work.
    """
    pass


class TimestampMixin:
    """
    Adds created_at and updated_at to any model that inherits it.

    Why a mixin:
        DRY — define timestamp columns once, reuse across all models.
        server_default=func.now() means PostgreSQL sets the value,
        not Python — works even for direct SQL inserts that bypass the ORM.

    Usage:
        class Project(TimestampMixin, Base):
            ...
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
