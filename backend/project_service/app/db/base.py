from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Single shared declarative base for all SQLAlchemy models.

    Why one Base across the entire service:
        Alembic imports Base.metadata to discover every table.
        If models used different Base instances, Alembic would only
        see the tables registered to the Base it imports — silently
        missing the others and never generating migrations for them.
    """
    pass


class TimestampMixin:
    """
    Reusable mixin that adds created_at and updated_at to any model.

    Why server_default=func.now() instead of default=datetime.utcnow:
        server_default tells PostgreSQL to set the value at the DB level.
        default tells Python to set the value before the INSERT.

        server_default is safer because:
        - It works even when rows are inserted directly via SQL (bypassing ORM)
        - The timestamp is set by the database clock, not the application clock
        - No timezone drift between app servers in a distributed setup

    Why DateTime(timezone=True):
        Stores timestamps as TIMESTAMPTZ in PostgreSQL.
        Always UTC-aware — no ambiguity when reading across timezones.
        Without timezone=True, you get naive datetimes that cause bugs
        when your app server and DB server are in different timezones.

    Usage:
        class Project(TimestampMixin, Base):
            __tablename__ = "projects"
            ...
        TimestampMixin must come BEFORE Base in the inheritance list
        so Python's MRO resolves the Mapped[] columns correctly.
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
