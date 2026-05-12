"""
Task Service — business logic layer.
CRUD implementations added in Phase 3.
"""
from uuid import UUID
from sqlalchemy.orm import Session
from app.repositories.task_repository import TaskRepository
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse, TaskSummary
from app.schemas.response_schema import PaginatedData


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self._repo = repository

    def get_task(self, task_id: UUID) -> TaskResponse:
        raise NotImplementedError

    def list_tasks(self, page: int = 1, page_size: int = 20) -> PaginatedData[TaskSummary]:
        raise NotImplementedError

    def list_tasks_by_project(self, project_id: UUID, page: int = 1, page_size: int = 20) -> PaginatedData[TaskSummary]:
        raise NotImplementedError

    def create_task(self, data: TaskCreate) -> TaskResponse:
        raise NotImplementedError

    def update_task(self, task_id: UUID, data: TaskUpdate) -> TaskResponse:
        raise NotImplementedError

    def delete_task(self, task_id: UUID) -> None:
        raise NotImplementedError


def get_task_service(db: Session) -> TaskService:
    return TaskService(TaskRepository(db))
