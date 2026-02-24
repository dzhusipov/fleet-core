from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(50, ge=1, le=200)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
