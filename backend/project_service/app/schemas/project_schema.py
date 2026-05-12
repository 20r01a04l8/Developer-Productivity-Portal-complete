from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.models.project import ProjectStatus


class ProjectCreate(BaseModel):
    """
    DTO for POST /projects.
    Only fields the client is allowed to set on creation.
    id, created_at, updated_at are never accepted from the client.
    """
    name: str = Field(..., min_length=1, max_length=255, examples=["Backend Platform"])
    owner: str = Field(..., min_length=1, max_length=255, examples=["alice@example.com"])
    status: ProjectStatus = Field(default=ProjectStatus.active)

    @field_validator("name", "owner", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class ProjectUpdate(BaseModel):
    """
    DTO for PATCH /projects/{id}.
    All fields optional — only provided fields are updated (partial update).
    """
    name: str | None = Field(default=None, min_length=1, max_length=255)
    owner: str | None = Field(default=None, min_length=1, max_length=255)
    status: ProjectStatus | None = None

    @field_validator("name", "owner", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str | None) -> str | None:
        return v.strip() if v else v


class ProjectResponse(BaseModel):
    """Full project DTO — used for single-item responses (GET /projects/{id})."""
    id: UUID
    name: str
    owner: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectSummary(BaseModel):
    """
    Lightweight DTO for list responses — omits timestamps to reduce payload size.
    Use ProjectResponse for detail views, ProjectSummary for list views.
    """
    id: UUID
    name: str
    owner: str
    status: ProjectStatus

    model_config = {"from_attributes": True}
