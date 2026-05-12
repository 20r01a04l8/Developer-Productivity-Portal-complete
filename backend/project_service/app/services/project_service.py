"""
Project Service — business logic layer.

Architecture rules:
    1. Never imports from fastapi (no HTTPException, no status codes).
    2. Raises domain exceptions from app.core.exceptions.
    3. Calls the repository — never writes SQL directly.
    4. Returns Pydantic schemas — never returns ORM models to the route layer.

CRUD implementations added in Phase 3.
"""
from uuid import UUID
from sqlalchemy.orm import Session
from app.repositories.project_repository import ProjectRepository
from app.schemas.project_schema import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectSummary
from app.schemas.response_schema import PaginatedData


class ProjectService:
    """Constructor injection — receives a repository, does not create one."""

    def __init__(self, repository: ProjectRepository) -> None:
        self._repo = repository

    def get_project(self, project_id: UUID) -> ProjectResponse:
        """Raises ProjectNotFoundError if not found."""
        raise NotImplementedError

    def list_projects(self, page: int = 1, page_size: int = 20) -> PaginatedData[ProjectSummary]:
        raise NotImplementedError

    def create_project(self, data: ProjectCreate) -> ProjectResponse:
        """Raises ProjectAlreadyExistsError if name is taken."""
        raise NotImplementedError

    def update_project(self, project_id: UUID, data: ProjectUpdate) -> ProjectResponse:
        """Raises ProjectNotFoundError if not found."""
        raise NotImplementedError

    def delete_project(self, project_id: UUID) -> None:
        """Raises ProjectNotFoundError if not found."""
        raise NotImplementedError


def get_project_service(db: Session) -> ProjectService:
    """
    Factory — wires repository into service.
    Used by the dependency injection container in api/deps.py.
    """
    return ProjectService(ProjectRepository(db))
