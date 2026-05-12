"""
Task Repository — data access layer.
CRUD implementations added in Phase 3.
"""
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task_schema import TaskCreate, TaskUpdate


class TaskRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, task_id: UUID) -> Task | None:
        raise NotImplementedError

    def get_all(self, skip: int = 0, limit: int = 20) -> tuple[list[Task], int]:
        raise NotImplementedError

    def get_by_project(self, project_id: UUID, skip: int = 0, limit: int = 20) -> tuple[list[Task], int]:
        raise NotImplementedError

    def create(self, data: TaskCreate) -> Task:
        raise NotImplementedError

    def update(self, task: Task, data: TaskUpdate) -> Task:
        raise NotImplementedError

    def delete(self, task: Task) -> None:
        raise NotImplementedError
