from typing import TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None = None


class PaginatedData(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: PaginatedData[T] | None = None
