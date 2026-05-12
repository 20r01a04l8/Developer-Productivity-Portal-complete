import uuid
import enum
from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, TimestampMixin


class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Task(TimestampMixin, Base):
    """
    project_id is a logical foreign key only — no DB-level constraint.
    The two services have separate databases so a DB FK is impossible.
    The service layer validates project_id by calling Project Service.
    """
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus, name="taskstatus"),
        nullable=False,
        default=TaskStatus.todo,
    )
    priority: Mapped[TaskPriority] = mapped_column(
        SAEnum(TaskPriority, name="taskpriority"),
        nullable=False,
        default=TaskPriority.medium,
    )

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title!r} status={self.status}>"
