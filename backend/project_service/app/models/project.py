import uuid
import enum

from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base, TimestampMixin


# ── Status Enum ───────────────────────────────────────────────────────────────

class ProjectStatus(str, enum.Enum):
    """
    Why (str, enum.Enum) and not just enum.Enum:

        Plain enum.Enum:
            ProjectStatus.active == "active"  →  False
            JSON serialisation requires a custom encoder

        str + enum.Enum:
            ProjectStatus.active == "active"  →  True
            Pydantic validates "active" from JSON directly against this enum
            SQLAlchemy stores and reads the plain string value from PostgreSQL
            No custom JSON encoder needed anywhere

    The three lifecycle states a project can be in:
        active    — currently being worked on
        archived  — paused or deprioritised, not deleted
        completed — all work finished
    """
    active = "active"
    archived = "archived"
    completed = "completed"


# ── ORM Model ─────────────────────────────────────────────────────────────────

class Project(TimestampMixin, Base):
    """
    SQLAlchemy ORM model for the `projects` table.

    ── How ORM models work ──────────────────────────────────────────────────

    This class is a Python mirror of a database table.
    Each class attribute with mapped_column() maps to one column.

    When you write:
        project = db.query(Project).filter(Project.id == some_id).first()

    SQLAlchemy translates that to:
        SELECT id, name, owner, status, created_at, updated_at
        FROM projects
        WHERE id = 'some_id'
        LIMIT 1;

    You get back a Project instance where:
        project.id      →  uuid.UUID
        project.name    →  str
        project.status  →  ProjectStatus.active

    The ORM handles all SQL generation, parameter binding, and type
    conversion. You never write raw SQL in the application layer.

    ── Why TimestampMixin comes before Base ─────────────────────────────────

    Python resolves inheritance left to right (MRO).
    TimestampMixin defines created_at and updated_at as Mapped[] columns.
    Placing it before Base ensures SQLAlchemy registers those columns
    as part of this table's definition.

    ── SQLAlchemy 2.0 Mapped[] syntax ───────────────────────────────────────

    Old (1.x) style:
        id = Column(UUID(as_uuid=True), primary_key=True)
        # type: Any — your IDE has no idea what this is

    New (2.0) style:
        id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
        # type: uuid.UUID — full IDE autocomplete and type checking

    The new style catches type bugs at development time, not at runtime.
    """

    __tablename__ = "projects"

    # ── Primary Key ───────────────────────────────────────────────────────────
    #
    # Why UUID instead of integer auto-increment:
    #
    #   Security:
    #       Integer IDs expose record counts.
    #       GET /projects/1, /projects/2, /projects/3 tells an attacker
    #       exactly how many projects exist and lets them enumerate all of them.
    #       UUID IDs (e.g. 550e8400-e29b-41d4-a716-446655440000) reveal nothing.
    #
    #   Distributed systems:
    #       Integer IDs require a central sequence generator — one DB must own
    #       the counter. UUID v4 is randomly generated and statistically unique
    #       across all services, all databases, all time.
    #       Two services can generate IDs independently with no coordination.
    #
    #   Microservice boundaries:
    #       Task Service stores project_id as a UUID reference.
    #       If Project Service used integer IDs, project_id=1 in Task DB and
    #       project_id=1 in a future third service could mean different things.
    #       UUIDs are globally unique — no collision risk.
    #
    #   default=uuid.uuid4:
    #       The UUID is generated in Python before the INSERT.
    #       This means you know the ID before the DB round-trip completes,
    #       which is useful for returning the ID in the response immediately.
    #
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # ── Business Fields ───────────────────────────────────────────────────────
    #
    # String(255): matches VARCHAR(255) in PostgreSQL.
    # 255 is a practical limit — long enough for any real project name,
    # short enough to be indexed efficiently.
    #
    # nullable=False: enforced at the database level, not just application level.
    # Even if someone inserts a row directly via SQL, the DB rejects null values.
    #
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    owner: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # SAEnum with name="projectstatus":
    #   Creates a named PostgreSQL ENUM type called "projectstatus".
    #   Named enums can be referenced by name in migrations and altered later.
    #   Anonymous enums (without name=) cause issues during Alembic migrations.
    #
    status: Mapped[ProjectStatus] = mapped_column(
        SAEnum(ProjectStatus, name="projectstatus"),
        nullable=False,
        default=ProjectStatus.active,
    )

    # created_at and updated_at are inherited from TimestampMixin.
    # They do not need to be declared here.
    # Why timestamps matter:
    #
    #   Auditing:
    #       "When was this project created?" and "When was it last changed?"
    #       are questions every production system must answer.
    #       Without timestamps, you cannot answer them — ever.
    #
    #   Debugging:
    #       When an incident occurs, timestamps let you reconstruct
    #       the exact sequence of events. "The project was archived at 14:32,
    #       three minutes before the deployment failed."
    #
    #   Sorting:
    #       Default list ordering is almost always "newest first" or
    #       "recently updated first". Without created_at/updated_at,
    #       you have no reliable way to sort.
    #
    #   Soft deletes (future):
    #       If you add a deleted_at column later, you can implement
    #       soft deletes without losing the original timestamps.
    #
    #   Data sync:
    #       If a frontend or external system needs to sync changes,
    #       it queries "give me everything updated_at > last_sync_time".
    #       Without updated_at, incremental sync is impossible.

    # ── Utility ───────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        """
        Human-readable string for logs and debugger output.

        Without __repr__:
            <app.models.project.Project object at 0x000001A2B3C4D5E6>

        With __repr__:
            <Project id=550e8400-e29b-41d4 name='Backend Platform' status=active>

        This makes log lines and pytest failure output immediately readable.
        """
        return (
            f"<Project id={self.id} name={self.name!r} status={self.status}>"
        )
