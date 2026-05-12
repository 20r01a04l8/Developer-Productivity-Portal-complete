"""
Dependency injection wiring for Task Service.
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.task_service import TaskService, get_task_service


def get_task_service_dep(db: Session = Depends(get_db)) -> TaskService:
    """
    Wires the full dependency chain:
        get_db() → Session → TaskRepository → TaskService
    """
    return get_task_service(db)
