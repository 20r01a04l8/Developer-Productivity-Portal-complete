"""
Dependency injection wiring for Project Service.

Why this file exists:
    Routes declare what they need. This file builds it.
    If you change how the service is constructed, you change it here only.
    All routes are untouched — Dependency Inversion Principle.

Usage in a route:
    from app.api.deps import get_project_service_dep

    @router.get("/projects")
    def list_projects(service: ProjectService = Depends(get_project_service_dep)):
        ...
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.project_service import ProjectService, get_project_service


def get_project_service_dep(db: Session = Depends(get_db)) -> ProjectService:
    """
    Wires the full dependency chain:
        get_db() → Session → ProjectRepository → ProjectService
    """
    return get_project_service(db)
