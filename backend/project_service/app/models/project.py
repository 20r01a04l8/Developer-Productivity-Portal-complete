import uuid
import enum
from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, TimestampMixin


class ProjectStatus(str, enum.Enum):
    """
    str + enum.Enum: the value IS the string.
    ProjectStatus.active == "active" → True
    Makes JSON serialisation and Pydantic validation seamless.
    """
    active = "active"
    archived = "archived"
    completed = "completed"


class Project(TimestampMixin, Base):
    """
    SQLAlchemy 2.0 ORM model using Mapped[] for full IDE type inference.
    TimestampMixin adds created_at and updated_at automatically.
    """
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ProjectStatus] = mapped_column(
        SAEnum(ProjectStatus, name="projectstatus"),
        nullable=False,
        default=ProjectStatus.active,
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} name={self.name!r} status={self.status}>"
