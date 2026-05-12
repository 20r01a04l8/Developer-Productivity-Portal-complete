from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.models.task import TaskStatus, TaskPriority


class TaskCreate(BaseModel):
    project_id: UUID
    title: str = Field(..., min_length=1, max_length=255, examples=["Set up CI pipeline"])
    status: TaskStatus = Field(default=TaskStatus.todo)
    priority: TaskPriority = Field(default=TaskPriority.medium)

    @field_validator("title", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None

    @field_validator("title", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str | None) -> str | None:
        return v.strip() if v else v


class TaskResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskSummary(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    status: TaskStatus
    priority: TaskPriority

    model_config = {"from_attributes": True}
