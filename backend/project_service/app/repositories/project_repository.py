"""
Project Repository — data access layer.

Architecture rule:
    This is the ONLY place in the codebase that writes SQL queries.
    Services call repository methods. Routes call service methods.
    Neither services nor routes ever touch the DB session directly.

CRUD implementations added in Phase 3.
"""
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.project_schema import ProjectCreate, ProjectUpdate


class ProjectRepository:
    """
    Constructor injection — receives a Session, does not create one.
    In unit tests: pass a test session or mock instead of the real DB session.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, project_id: UUID) -> Project | None:
        raise NotImplementedError

    def get_all(self, skip: int = 0, limit: int = 20) -> tuple[list[Project], int]:
        """Returns (items, total_count) — both needed for pagination."""
        raise NotImplementedError

    def create(self, data: ProjectCreate) -> Project:
        raise NotImplementedError

    def update(self, project: Project, data: ProjectUpdate) -> Project:
        raise NotImplementedError

    def delete(self, project: Project) -> None:
        raise NotImplementedError

    def exists_by_name(self, name: str) -> bool:
        raise NotImplementedError
