from typing import TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """
    Standard envelope for ALL API responses — success and error.

    Every endpoint returns this shape:
        { "success": true|false, "message": "...", "data": <payload>|null }

    Why this matters:
        The frontend always reads response.data.success.
        No guessing whether the payload is at .data or .data.result.
        Error handling is uniform across all endpoints.
    """
    success: bool
    message: str
    data: T | None = None


class PaginatedData(BaseModel, Generic[T]):
    """Inner payload for paginated list responses."""
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Envelope for paginated list responses:
        {
            "success": true,
            "message": "Projects retrieved.",
            "data": {
                "items": [...],
                "total": 42,
                "page": 1,
                "page_size": 20,
                "pages": 3
            }
        }
    """
    success: bool
    message: str
    data: PaginatedData[T] | None = None
